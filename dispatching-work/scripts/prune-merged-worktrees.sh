#!/usr/bin/env bash
# prune-merged-worktrees.sh — classify, back up, and remove stale worktrees.
#
# Defaults to DRY-RUN. Pass --apply to actually remove.
# Expects a config file for protected paths (protected.list) in the repo root,
# one entry per line (branch name or worktree path).
#
# Usage: ./prune-merged-worktrees.sh [--apply] [--repo <path>]
set -euo pipefail

DRY_RUN=true
REPO_DIR="$(pwd)"
CONFIG_FILE="protected.list"
SKIP_LIVE_SESSIONS=true

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply) DRY_RUN=false ;;
    --repo) REPO_DIR="$2"; shift ;;
    --config) CONFIG_FILE="$2"; shift ;;
    --no-skip-live) SKIP_LIVE_SESSIONS=false ;;
    *) echo "Unknown arg $1"; exit 1 ;;
  esac
  shift
done

cd "${REPO_DIR:?REPO_DIR cannot be empty}"
echo "Repo: ${REPO_DIR:?}"
echo "Mode: $(${DRY_RUN} && echo DRY-RUN || echo APPLY)"

# Detect live agent sessions to avoid removing a running lane
is_live() {
  local path="$1"
  [ "$SKIP_LIVE_SESSIONS" = "false" ] && return 1
  # Heuristic: look for active lock files or claude session dirs
  if [ -d "${path}/.claude" ] && pgrep -f "claude.*$(basename "${path:?}")" > /dev/null 2>&1; then
     return 0
  fi
  return 1
}

WORKTREES=$(git worktree list --porcelain | grep '^worktree ' | sed 's/^worktree //' || true)
if [ -z "$WORKTREES" ]; then
  echo "No worktrees found."
  exit 0
fi

for WORKTREE in $WORKTREES; do
  [ -d "$WORKTREE" ] || continue
  BRANCH=$(git -C "${WORKTREE:?}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "DETACHED")
  echo "---"
  echo "Worktree: ${WORKTREE:?} (Branch: ${BRANCH:?})"

  # 1. Protected list
  if [ -f "${CONFIG_FILE}" ] && grep -qxF "${BRANCH}" "${CONFIG_FILE}" 2>/dev/null; then
     echo "Status: [SKIPPED: PROTECTED]"
     continue
  fi

  # 2. Live sessions
  if is_live "${WORKTREE}"; then
     echo "Status: [SKIPPED: LIVE SESSION]"
     continue
  fi

  # 3. Classify
  MERGE_STATUS="local-only"
  BASE=$(git merge-base main HEAD 2>/dev/null || echo "none")
  if [ "$BASE" != "none" ]; then
     if git merge-base --is-ancestor "${BRANCH}" main 2>/dev/null; then
        MERGE_STATUS="merged"
     elif git ls-remote origin "${BRANCH}" 2>/dev/null | grep -q "${BRANCH}"; then
        # Check if the remote branch is merged or if the PR is merged
        if git ls-remote --merged origin "${BRANCH}" 2>/dev/null | grep -q .; then
           MERGE_STATUS="pr-merged"
        else
           MERGE_STATUS="open"
        fi
     fi
  fi

  # 4. Check dirty state
  if [ -n "$(git -C "${WORKTREE:?}" status --porcelain 2>/dev/null)" ]; then
     echo "State: DIRTY"
     DIRTY=true
  else
     echo "State: CLEAN"
     DIRTY=false
  fi
  echo "Classification: ${MERGE_STATUS:?} / ${DIRTY:?}"

  # 5. Backup (if dirty)
  if [ "$DIRTY" = "true" ]; then
     BACKUP_DIR="${REPO_DIR}/backups/worktrees"
     mkdir -p "${BACKUP_DIR:?}"
     TS=$(date +%Y%m%d-%H%M%S)
     SAFE_BRANCH=$(echo "${BRANCH:?}" | tr '/' '_')
     BACKUP_PATH="${BACKUP_DIR:?}/${SAFE_BRANCH:?}-${TS:?}.tgz"
     echo "Backing up ignored/untracked small files to ${BACKUP_PATH:?}"
     tar -czf "${BACKUP_PATH:?}" -C "${WORKTREE:?}" --exclude='.git' --exclude='node_modules' --exclude='dist' --exclude='build' --exclude='.venv' --exclude='__pycache__' . 2>/dev/null || true
  fi

  # 6. Removal
  if [ "$DRY_RUN" = "false" ]; then
     if [ "$MERGE_STATUS" = "merged" ] || [ "$MERGE_STATUS" = "pr-merged" ]; then
        echo "ACTION: Removing worktree ${WORKTREE:?}"
        orca worktree rm --force "${WORKTREE:?}" 2>/dev/null || git worktree remove --force "${WORKTREE:?}" || true
        git branch -D "${BRANCH:?}" 2>/dev/null || true
     fi
  fi
done

git worktree prune
echo "Prune pass complete."
