#!/usr/bin/env bash
# Watch an Orca orchestration mailbox: wake when a message is waiting or a lane
# deadline goes overdue. Silence is not progress.

set -u

usage() {
  cat <<'EOF'
watch-inbox.sh — wake an Orca coordinator or PM when its orchestration mailbox
has a message, or when a deadline in its ledger goes overdue.

This is for Orca's orchestration mailbox. Run it as a background task; when it
exits, drain and ack the mailbox, then start it again.

Options:
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
check or a failed runtime call never exits the watcher; it logs one line to
stderr, sleeps 60s and retries.
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

run_id="${ORCA_RUN_ID:-}"
ledger="${DEADLINE_LEDGER:-}"
types="worker_done,escalation,question,status,merge_ready"
window=10800
poll=1800

while [ $# -gt 0 ]; do
  case "$1" in
    --run) need_value "$1" "${2:-}"; run_id=$2; shift 2 ;;
    --ledger) need_value "$1" "${2:-}"; ledger=$2; shift 2 ;;
    --types) need_value "$1" "${2:-}"; types=$2; shift 2 ;;
    --window) need_int "$1" "${2:-}"; window=$2; shift 2 ;;
    --poll-secs) need_int "$1" "${2:-}"; poll=$2; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "watch-inbox.sh: unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [ -z "$run_id" ]; then
  echo "watch-inbox.sh: no run id given: pass --run or set ORCA_RUN_ID" >&2
  exit 2
fi

dir=$(cd "$(dirname "$0")" && pwd)

end=$(( $(date +%s) + window ))
while [ "$(date +%s)" -lt "$end" ]; do
  nxt=""
  if [ -n "$ledger" ]; then
    dl=$(python3 "$dir/deadlines.py" --ledger "$ledger" --new)
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
    nxt=$(python3 "$dir/deadlines.py" --ledger "$ledger" --next 2>/dev/null)
  fi
  ms=$(( poll * 1000 ))
  if [ -n "$nxt" ] && [ "$nxt" -lt "$poll" ]; then ms=$(( (nxt + 5) * 1000 )); fi
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
