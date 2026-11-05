#!/usr/bin/env bash
# prune-merged-worktrees.sh — classify, back up, and remove stale git worktrees.
#
# DRY-RUN by default: classifies every worktree and prints the plan; writes
# nothing. Pass --apply to back up and remove. Removal is limited to worktrees
# classified merged or PR-merged; closed / open / local-only are only reported.
#
# Classification:
#   merged     — the worktree's HEAD is an ancestor of the merge target
#   pr-merged  — gh reports the branch's PR merged (when gh is available)
#   closed     — gh reports the branch's PR closed without merging
#   open       — the branch exists on the origin remote and is not merged
#   local-only — the branch exists only locally
# Each worktree is also clean or dirty (tracked edits, untracked or ignored
# files). Ignored files alone do not make a worktree dirty to git, but they
# are the most common unique state a removal destroys, so they are backed up
# too.
#
# Safety guards:
#   - dry run is the default; --apply is the only writing mode
#   - --apply is refused when the invoking shell's toplevel is the repo's
#     primary (live) checkout unless --confirm-live-checkout is passed
#   - the primary checkout and the worktree containing the invoking shell are
#     never removal candidates
#   - backups are written outside the repo (a sibling directory by default)
#   - the protected list (--config file: branch names or worktree paths, one
#     per line, '#' comments) is always skipped
#   - worktrees with a live agent session are skipped (heuristic: a process
#     whose command line contains the worktree path, or a recent session file
#     under the known agent session directories)
#   - every removal and branch-deletion target is guarded with ${VAR:?}
#
# Usage:
#   prune-merged-worktrees.sh                       # dry run, current repo
#   prune-merged-worktrees.sh --apply [--confirm-live-checkout]
#   prune-merged-worktrees.sh [--repo <path>] [--base <ref>] [--config <file>]
#                             [--backup-dir <dir>] [--live-minutes <n>]
#                             [--no-skip-live] [--include-closed]
#
# Exit codes: 0 on success (including a dry run), 1 on refusal or error.
set -euo pipefail

APPLY=false
REPO_DIR=""
BASE=""
BASE_REF=""
CONFIG=""
BACKUP_ROOT=""
LIVE_MINUTES=30
SKIP_LIVE=true
CONFIRM_LIVE=false
INCLUDE_CLOSED=false
MAX_FILE_BYTES=$((10 * 1024 * 1024))   # "small files" cap per backed-up file
GH_BIN="${GH_BIN:-gh}"

die() { echo "ERROR: $*" >&2; exit 1; }
info() { echo "$*"; }

# ---------- argument parsing ----------
while [ $# -gt 0 ]; do
  case "$1" in
    --apply) APPLY=true ;;
    --repo) [ $# -ge 2 ] || die "--repo needs a path"; REPO_DIR=$2; shift ;;
    --base) [ $# -ge 2 ] || die "--base needs a ref"; BASE=$2; shift ;;
    --config) [ $# -ge 2 ] || die "--config needs a path"; CONFIG=$2; shift ;;
    --backup-dir) [ $# -ge 2 ] || die "--backup-dir needs a path"; BACKUP_ROOT=$2; shift ;;
    --live-minutes) [ $# -ge 2 ] || die "--live-minutes needs a number"; LIVE_MINUTES=$2; shift ;;
    --no-skip-live) SKIP_LIVE=false ;;
    --confirm-live-checkout) CONFIRM_LIVE=true ;;
    --include-closed) INCLUDE_CLOSED=true ;;
    -h|--help) awk 'NR>1 && /^set -euo/{exit} NR>1{print}' "$0"; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
  shift
done

[ -n "${REPO_DIR:-}" ] || REPO_DIR="$(pwd)"
REPO_DIR="$(cd "${REPO_DIR:?}" && pwd -P)"
GIT=(git -C "${REPO_DIR:?}")
"${GIT[@]}" rev-parse --show-toplevel >/dev/null 2>&1 || die "not a git repository: ${REPO_DIR:?}"

# ---------- merge target ----------
if [ -z "$BASE" ]; then
  BASE="$("${GIT[@]}" symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||' || true)"
  if [ -z "$BASE" ]; then
    for cand in main master; do
      if "${GIT[@]}" show-ref --verify --quiet "refs/heads/${cand}" \
         || "${GIT[@]}" show-ref --verify --quiet "refs/remotes/origin/${cand}"; then
        BASE=$cand; break
      fi
    done
  fi
fi
[ -n "${BASE:-}" ] || die "cannot detect the merge target; pass --base <ref>"
if "${GIT[@]}" show-ref --verify --quiet "refs/remotes/origin/${BASE:?}"; then
  BASE_REF="refs/remotes/origin/${BASE:?}"
elif "${GIT[@]}" show-ref --verify --quiet "refs/heads/${BASE:?}"; then
  BASE_REF="refs/heads/${BASE:?}"
else
  die "merge target ${BASE:?} does not exist"
fi
info "Repo: ${REPO_DIR:?}   Merge target: ${BASE_REF:?}   Mode: $([ "${APPLY:?}" = true ] && echo APPLY || echo DRY-RUN)"

# ---------- live-checkout write guard ----------
# The primary checkout is the live checkout the lanes must never write in. A
# lane wrongly dispatched there is stopped here; a coordinator pruning from the
# live checkout passes --confirm-live-checkout.
PRIMARY=""
CWD_TOP="$(git rev-parse --show-toplevel 2>/dev/null || true)"
detect_primary() {
  # line-by-line read: an unquoted for-in word-splits paths containing spaces,
  # which silently emptied PRIMARY and defeated the live-checkout refusal
  "${GIT[@]}" worktree list --porcelain | sed -n 's/^worktree //p' | while IFS= read -r wt; do
    if [ -d "${wt}/.git" ]; then
      echo "${wt}"
      break
    fi
  done
}
PRIMARY="$(detect_primary)"
if [ "${APPLY:?}" = true ] && [ -n "${CWD_TOP}" ] && [ -n "${PRIMARY}" ] \
   && [ "${CWD_TOP}" = "${PRIMARY}" ] && [ "${CONFIRM_LIVE}" = false ]; then
  die "--apply refused: the working directory's toplevel (${CWD_TOP}) is the repo's live checkout (the primary working tree). Lanes must never write there. Run from a lane worktree, or pass --confirm-live-checkout if you are the coordinator pruning from here."
fi

# ---------- backup root ----------
if [ -z "$BACKUP_ROOT" ]; then
  BACKUP_ROOT="$(dirname "${REPO_DIR:?}")/worktree-backups"
fi
BACKUP_ROOT="$(cd "$(dirname "${BACKUP_ROOT:?}")" && pwd -P)/$(basename "${BACKUP_ROOT:?}")"
case "${BACKUP_ROOT:?}/" in
  "${REPO_DIR:?}"/*) die "--backup-dir must live outside the repository (${REPO_DIR:?}), not inside it" ;;
esac

# ---------- protected list ----------
protected_entries=()
if [ -z "$CONFIG" ] && [ -f "${REPO_DIR:?}/.protected-worktrees" ]; then
  CONFIG="${REPO_DIR:?}/.protected-worktrees"
fi
if [ -n "${CONFIG:-}" ]; then
  if [ -f "${CONFIG:?}" ]; then
    while IFS= read -r line; do
      case "${line}" in ''|\#*) continue ;; esac
      # resolve path entries so they match git's canonical worktree paths
      if [ -d "${line}" ]; then
        line="$(cd "${line}" 2>/dev/null && pwd -P)" || true
      fi
      protected_entries+=("${line}")
    done < "${CONFIG:?}"
  else
    die "config file not found: ${CONFIG:?}"
  fi
fi
is_protected() {
  local candidate=$1
  local entry
  for entry in ${protected_entries[@]+"${protected_entries[@]}"}; do
    [ "${candidate}" = "${entry}" ] && return 0
  done
  return 1
}

# ---------- live-session heuristic ----------
is_live() {
  [ "${SKIP_LIVE}" = false ] && return 1
  local wt=$1
  # 1. a process whose command line mentions the worktree path
  pgrep -f -- "${wt}" >/dev/null 2>&1 && return 0
  # 2. a session file newer than the reference time under a known agent
  #    session directory (claudes and pis munge the worktree path with
  #    dashes, so a contains-match finds both)
  local munged base d f
  munged="${wt//\//-}"
  for base in "${HOME:-}/.claude/projects" "${HOME:-}/.pi/agent/sessions"; do
    [ -d "${base}" ] || continue
    for d in "${base}"/*"${munged}"*; do
      [ -d "${d}" ] || continue
      for f in "${d}"/*.jsonl "${d}"/*/*.jsonl; do
        [ -f "${f}" ] || continue
        [ "${f}" -nt "${REF_FILE:?}" ] && return 0
      done
    done
  done
  return 1
}

# reference time = now minus LIVE_MINUTES; every session file newer than it
# marks a live session. If the timestamp cannot be computed, fall back to
# /dev/null (ancient mtime), which treats every session file as live - the
# fail-safe direction.
REF_FILE=/dev/null
if [ "${SKIP_LIVE}" = true ]; then
  REF_TS="$(date -v-"${LIVE_MINUTES}"M +%Y%m%d%H%M 2>/dev/null || date -d "${LIVE_MINUTES} minutes ago" +%Y%m%d%H%M 2>/dev/null || true)"
  if [ -n "${REF_TS}" ]; then
    REF_FILE="$(mktemp "${TMPDIR:-/tmp}/prune-ref.XXXXXX")"
    touch -t "${REF_TS}" "${REF_FILE}"
    trap 'rm -f "${REF_FILE:?}"' EXIT
  else
    info "WARNING: --live-minutes '${LIVE_MINUTES}' is not a usable offset; treating every session file as live (fail-safe)."
  fi
fi

# ---------- classification ----------
classify() {
  local sha=$1 branch=$2
  if "${GIT[@]}" merge-base --is-ancestor "${sha}" "${BASE_REF}" >/dev/null 2>&1; then
    echo merged; return
  fi
  local origin_url=""
  origin_url="$("${GIT[@]}" remote get-url origin 2>/dev/null || true)"
  if command -v "${GH_BIN}" >/dev/null 2>&1 && [ -n "${origin_url}" ]; then
    local state
    state="$("${GH_BIN}" -R "${origin_url}" pr list --head "${branch}" --state all --json state,headRefOid --jq "[.[] | select(.headRefOid == \"${sha}\")] | if length > 0 then .[0].state else \"\" end" 2>/dev/null || true)"
    case "${state}" in
      MERGED) echo pr-merged; return ;;
      CLOSED) echo closed; return ;;
      OPEN) echo open; return ;;
    esac
  fi
  if "${GIT[@]}" ls-remote --exit-code --heads origin "refs/heads/${branch}" >/dev/null 2>&1; then
    echo open; return
  fi
  echo local-only
}

dirty_state() {
  local wt=$1
  if [ -n "$("${GIT[@]}" -C "${wt}" status --porcelain 2>/dev/null)" ]; then
    echo dirty
  else
    echo clean
  fi
}

# ---------- backup ----------
backup_worktree() {
  local wt=$1 branch=$2
  local safe backup_dir n_files=0
  safe="$(printf '%s' "${branch:-detached-$(basename "${wt}")}" | tr '/' '_')"
  backup_dir="${BACKUP_ROOT}/${safe}-$(date +%Y%m%d-%H%M%S)"
  mkdir -p "${backup_dir}"
  info "Backing up untracked and ignored files to ${backup_dir}"
  # dirty tracked changes as a patch
  if [ -n "$("${GIT[@]}" -C "${wt}" diff HEAD 2>/dev/null)" ]; then
    "${GIT[@]}" -C "${wt}" diff HEAD > "${backup_dir}/dirty-tracked.patch"
  fi
  # untracked and ignored files, skipping anything over MAX_FILE_BYTES
  local f size
  while IFS= read -r -d '' f; do
    [ -f "${wt}/${f}" ] || continue
    size=$(wc -c < "${wt}/${f}")
    if [ "${size}" -gt "${MAX_FILE_BYTES}" ]; then
      info "NOT backed up (over cap): ${f} (${size} bytes)"
      continue
    fi
    mkdir -p "${backup_dir}/$(dirname "${f}")"
    cp -p "${wt}/${f}" "${backup_dir}/${f}"
    n_files=$((n_files + 1))
  done < <("${GIT[@]}" -C "${wt}" ls-files --others --exclude-standard -z
           "${GIT[@]}" -C "${wt}" ls-files --others --ignored --exclude-standard -z)
  info "Backed up ${n_files} file(s)."
  [ "${n_files}" -gt 0 ] || rmdir "${backup_dir}" 2>/dev/null || true
}

# ---------- worktree records ----------
# porcelain records: worktree <path> / HEAD <sha> / branch refs/heads/<name>
# or detached / bare / blank line separators.
wts=(); shas=(); branches=()
cur_wt=""; cur_sha=""; cur_branch=""
flush_record() {
  if [ -n "${cur_wt}" ]; then
    # canonicalize: git resolves symlinks when recording worktree paths, so
    # every comparison (config entries, cwd checks, session munging) must use
    # the same resolved form
    local resolved
    resolved="$(cd "${cur_wt}" 2>/dev/null && pwd -P)" || resolved="${cur_wt}"
    wts+=("${resolved}"); shas+=("${cur_sha}"); branches+=("${cur_branch}")
  fi
  cur_wt=""; cur_sha=""; cur_branch=""
}
while IFS= read -r line; do
  case "${line}" in
    worktree\ *) flush_record; cur_wt="${line#worktree }" ;;
    HEAD\ *) cur_sha="${line#HEAD }" ;;
    branch\ *) cur_branch="${line#branch refs/heads/}" ;;
    detached) cur_branch="" ;;
    bare) cur_branch="" ;;
    '') flush_record ;;
  esac
done < <("${GIT[@]}" worktree list --porcelain)
flush_record

[ "${#wts[@]}" -gt 0 ] || { info "No worktrees found."; exit 0; }

# ---------- main pass ----------
removed_any=false
i=0
while [ "${i}" -lt "${#wts[@]}" ]; do
  wt="${wts[${i}]}"; sha="${shas[${i}]}"; branch="${branches[${i}]}"
  i=$((i + 1))

  echo "---"
  if [ ! -d "${wt}" ]; then
    echo "Worktree: ${wt} — missing directory (prunable)"; continue
  fi

  echo "Worktree: ${wt}   Branch: ${branch:-DETACHED}"

  # never touch the primary (live) checkout
  if [ -d "${wt}/.git" ]; then
    echo "Status: [SKIPPED: PRIMARY / LIVE CHECKOUT]"; continue
  fi
  # never remove the tree the invoking shell sits in
  if [ -n "${CWD_TOP}" ] && [ "${CWD_TOP}" = "${wt}" ]; then
    echo "Status: [SKIPPED: CURRENT WORKING TREE]"; continue
  fi
  # protected list: branch name or worktree path
  if is_protected "${branch}" || is_protected "${wt}"; then
    echo "Status: [SKIPPED: PROTECTED]"; continue
  fi
  # live agent session
  if is_live "${wt}"; then
    echo "Status: [SKIPPED: LIVE SESSION]"; continue
  fi

  state="$(dirty_state "${wt}")"
  class="$(classify "${sha}" "${branch}")"
  echo "Classification: ${class} / ${state}"

  case "${class}" in
    closed)
      [ "${INCLUDE_CLOSED}" = true ] || { echo "Action: none (closed PR — review before removing)"; continue; }
      ;;
    open|local-only)
      echo "Action: none (not merged — review before removing)"; continue
      ;;
  esac

  if [ "${APPLY}" = false ]; then
    echo "Action: WOULD back up untracked/ignored files, then remove worktree${branch:+ and delete branch ${branch}} (dry run)"
    continue
  fi

  backup_worktree "${wt}" "${branch}"
  info "Removing worktree ${wt}"
  if orca worktree rm --force "${wt:?}" 2>/dev/null \
     || "${GIT[@]}" worktree remove --force -- "${wt:?}"; then
    removed_any=true
  else
    echo "ERROR: failed to remove worktree ${wt} — left in place" >&2
    continue
  fi
  if [ -n "${branch}" ]; then
    if "${GIT[@]}" branch -d "${branch:?}" >/dev/null 2>&1; then
      info "Deleted branch ${branch}"
    else
      echo "NOTE: branch ${branch} kept (git refused deletion)"
    fi
  fi
done

echo "---"
if [ "${APPLY}" = true ]; then
  "${GIT[@]}" worktree prune
fi
if [ "${APPLY}" = true ] && [ "${removed_any}" = true ]; then
  info "Backups live outside the repo under ${BACKUP_ROOT}."
fi
info "Prune pass complete."
