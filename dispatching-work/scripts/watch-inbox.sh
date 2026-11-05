#!/usr/bin/env bash
# Watch a runtime signal: wake when a message is waiting or a lane
# deadline goes overdue. Silence is not progress.

set -u

usage() {
  cat <<'EOF'
watch-inbox.sh — wake a coordinator or PM on a runtime signal or overdue lane.

This is for Orca's orchestration mailbox. Run it as a background task; when it
exits, drain and ack the mailbox, then start it again.

Herdr mode watches an assigned agent's settled state, or literal pane output.
It has no mailbox: after waking, read the bound report and record its receipt.
Idle/done/blocked and historical output matches are signals, not task verdicts.
Requires HERDR_ENV=1. Timeout errors retry; other herdr errors fail visibly.

Options:
  --runtime NAME orca (default) or herdr; also $MUSTER_RUNTIME
  --target ID    herdr agent name or pane ID (required in herdr mode)
  --match TEXT   use pane wait-output instead of agent wait (literal text)
  --run ID       orchestration run id to watch (default: $ORCA_RUN_ID)
  --ledger PATH  deadline ledger to poll with deadlines.py
                 (default: $DEADLINE_LEDGER; no ledger = mailbox only)
  --types LIST   comma-separated message types to wake on
                 (default: worker_done,escalation,question,status,merge_ready)
  --window N     overall watching window in seconds (default: 10800 = 3h)
  --poll-secs N  maximum mailbox wait between polls (default: 1800)

Uses --peek throughout: it never acknowledges or consumes a delivery — the
agent reads and acks after it wakes. It exits 0 printing the message summary
when a message is waiting, and exits 0 printing the overdue report when a
deadline is NEW (reported once; a seen-file beside the ledger keeps track).
Otherwise it keeps waiting, surviving runtime restarts and lost connections by
sleeping and retrying, until the window ends; then it prints one
"WATCH: no message within window" line and exits 0. Ledger format is in
deadlines.py --help.

The deadline report is one-shot: a deadline the watcher has reported is never
re-raised. If a wake is missed, recover by running deadlines.py with the same
--ledger but without --new — it lists every overdue lane. A failed deadline
check or failed Orca call logs to stderr and retries after 60s. Herdr timeouts
re-arm within the window; other herdr errors exit 1 for reconciliation.
EOF
}

need_value() { # $1 = option name, $2 = value
  if [ $# -lt 2 ] || [ -z "$2" ]; then
    echo "watch-inbox.sh: $1 needs a value" >&2
    usage >&2
    exit 2
  fi
}

need_int() { # $1 = option name, $2 = value
  need_value "$@"
  case "$2" in
    ''|*[!0-9]*)
      echo "watch-inbox.sh: $1 needs a positive integer, got: $2" >&2
      usage >&2
      exit 2 ;;
  esac
}

runtime="${MUSTER_RUNTIME:-orca}"
target=""
match=""
run_id="${ORCA_RUN_ID:-}"
ledger="${DEADLINE_LEDGER:-}"
types="worker_done,escalation,question,status,merge_ready"
window=10800
poll=1800

while [ $# -gt 0 ]; do
  case "$1" in
    --runtime) need_value "$1" "${2:-}"; runtime=$2; shift 2 ;;
    --target) need_value "$1" "${2:-}"; target=$2; shift 2 ;;
    --match) need_value "$1" "${2:-}"; match=$2; shift 2 ;;
    --run) need_value "$1" "${2:-}"; run_id=$2; shift 2 ;;
    --ledger) need_value "$1" "${2:-}"; ledger=$2; shift 2 ;;
    --types) need_value "$1" "${2:-}"; types=$2; shift 2 ;;
    --window) need_int "$1" "${2:-}"; window=$2; shift 2 ;;
    --poll-secs) need_int "$1" "${2:-}"; poll=$2; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "watch-inbox.sh: unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

case "$runtime" in
  orca) ;;
  herdr)
    if [ "${HERDR_ENV:-}" != 1 ] || [ -z "$target" ]; then
      echo "watch-inbox.sh: herdr requires HERDR_ENV=1 and --target" >&2
      exit 2
    fi ;;
  *) echo "watch-inbox.sh: unknown runtime: $runtime" >&2; exit 2 ;;
esac
if [ "$runtime" = orca ] && [ -z "$run_id" ]; then
  echo "watch-inbox.sh: no run id given: pass --run or set ORCA_RUN_ID" >&2
  exit 2
fi

dir=$(cd "$(dirname "$0")" && pwd)

end=$(( $(date +%s) + window ))
while [ "$(date +%s)" -lt "$end" ]; do
  nxt=""
  if [ -n "$ledger" ]; then
    dl=$(python3 "$dir/deadlines.py" --runtime "$runtime" --ledger "$ledger" --new)
    rc=$?
    if [ "$rc" -ne 0 ]; then
      if printf '%s\n' "$dl" | grep -q '^OVERDUE'; then
        printf '%s\n' "$dl"
        exit 0
      fi
      echo "watch-inbox.sh: deadline check failed (rc=$rc) without an OVERDUE report; retrying in 60s" >&2
      sleep 60
      continue
    fi
    nxt=$(python3 "$dir/deadlines.py" --runtime "$runtime" --ledger "$ledger" --next 2>/dev/null)
  fi
  ms=$(( poll * 1000 ))
  if [ -n "$nxt" ] && [ "$nxt" -lt "$poll" ]; then ms=$(( (nxt + 5) * 1000 )); fi
  remaining=$(( (end - $(date +%s)) * 1000 ))
  if [ "$remaining" -le 0 ]; then break; fi
  if [ "$ms" -gt "$remaining" ]; then ms=$remaining; fi
  if [ "$runtime" = herdr ]; then
    if [ -n "$match" ]; then
      raw=$(herdr pane wait-output "$target" --match "$match" --source recent-unwrapped --timeout "$ms" 2>&1)
    else
      raw=$(herdr agent wait "$target" --timeout "$ms" 2>&1)
    fi
    rc=$?
    if [ "$rc" -eq 0 ]; then printf '%s\n' "$raw"; exit 0; fi
    if printf '%s' "$raw" | python3 -c 'import json,sys; sys.exit(0 if json.load(sys.stdin).get("error", {}).get("code") == "timeout" else 1)' 2>/dev/null; then
      continue
    fi
    printf 'watch-inbox.sh: herdr wait failed (rc=%s): %s\n' "$rc" "$raw" >&2
    exit 1
  fi
  raw=$(orca orchestration check --run "$run_id" --peek --wait --types "$types" \
        --timeout-ms "$ms" --json 2>&1)
  rc=$?
  out=$(printf '%s\n' "$raw" | grep -v _keepalive)
  if printf '%s\n' "$out" | grep -q '"count": *[1-9]'; then
    printf '%s\n' "$out" | cut -c1-600
    exit 0
  fi
  if [ "$rc" -ne 0 ] || ! printf '%s\n' "$out" | grep -q '"ok": *true'; then
    echo "watch-inbox.sh: orca orchestration check failed (rc=$rc): $(printf '%s\n' "$out" | head -n 1 | cut -c1-200)" >&2
    sleep 60
  elif printf '%s\n' "$out" | grep -q -E 'runtime_unavailable|waiter_exists|connectionLost": *true'; then
    sleep 60
  fi
done
echo "WATCH: no message within window"
exit 0
