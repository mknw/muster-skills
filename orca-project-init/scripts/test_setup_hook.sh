#!/usr/bin/env bash
# Run a repo's orca.yaml setup hook in a throwaway git worktree, exactly the way
# Orca will.
#
# Reading a setup hook does not tell you whether it works. This catches the
# things that only fail in a real second checkout: copy-source logic that
# assumed the primary path, steps that are not idempotent, `set -e` aborting on
# a false guard, and tools that were only ever on PATH in the primary shell.
#
# Usage:  test_setup_hook.sh [repo-path]      (defaults to the current repo)

set -euo pipefail

REPO="${1:-$(git rev-parse --show-toplevel)}"
REPO="$(cd "$REPO" && pwd)"
YAML="$REPO/orca.yaml"

[ -f "$YAML" ] || { echo "no orca.yaml at $YAML" >&2; exit 2; }

WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/orca-hooktest.XXXXXX")"
TREE="$WORKDIR/tree"
HOOK="$WORKDIR/setup.sh"

cleanup() {
  git -C "$REPO" worktree remove --force "$TREE" >/dev/null 2>&1 || true
  rm -rf "$WORKDIR"
}
trap cleanup EXIT

# Extract scripts.setup without assuming PyYAML is installed in the repo's env.
extract() {
  python3 -c '
import sys
try:
    import yaml
except ImportError:
    sys.exit(3)
d = yaml.safe_load(open(sys.argv[1], encoding="utf-8")) or {}
s = (d.get("scripts") or {}).get("setup")
if not s or not s.strip():
    sys.exit(4)
print(s)
' "$YAML" 2>/dev/null
}

# Capture the real exit code: `if ! extract` would collapse it to 0/1 and lose
# the difference between "PyYAML missing" (3) and "no setup hook" (4).
set +e
extract > "$HOOK"
status=$?
set -e

if [ "$status" -ne 0 ]; then
  if [ "$status" -eq 3 ]; then
    if command -v uv >/dev/null 2>&1; then
      uv run --quiet --with pyyaml python3 -c '
import sys, yaml
d = yaml.safe_load(open(sys.argv[1], encoding="utf-8")) or {}
print((d.get("scripts") or {}).get("setup") or "")
' "$YAML" > "$HOOK"
    else
      echo "PyYAML not available and no uv to borrow it from." >&2
      exit 2
    fi
  else
    echo "orca.yaml has no usable scripts.setup" >&2
    exit 2
  fi
fi

[ -s "$HOOK" ] || { echo "extracted an empty setup hook" >&2; exit 2; }

echo "repo:     $REPO"
echo "worktree: $TREE"
echo

# --detach so this never competes with a checked-out branch.
git -C "$REPO" worktree add --detach "$TREE" HEAD >/dev/null
echo "=== gitignored paths present before setup (expect none) ==="
# `[ -e ... ] && echo` here would make the loop exit non-zero on a false test and
# `set -e` would kill the script — the same trap this skill warns about in hooks.
git -C "$REPO" ls-files --others --ignored --exclude-standard --directory \
  | while read -r p; do
      if [ -e "$TREE/$p" ]; then echo "  $p"; fi
    done
echo

# Run with a SANITISED environment. Orca executes setup in a plain login shell,
# so tools your interactive shell gets from direnv, nix, mise, asdf, nvm or a
# virtualenv are NOT on PATH there. Running the hook from your own shell inherits
# all of that and hides the single most common failure: "uv: command not found"
# in the real worktree after a green local test.
CLEAN_PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
[ -d /run/current-system/sw/bin ] && CLEAN_PATH="$CLEAN_PATH:/run/current-system/sw/bin"
run_hook() {
  env -i HOME="$HOME" TERM="${TERM:-xterm}" PATH="$CLEAN_PATH" \
    /bin/sh -c "cd '$TREE' && sh '$HOOK'"
}

echo "=== run 1 (sanitised env — no direnv/nix/mise inherited) ==="
run_hook && echo "--- exit 0" || echo "--- EXIT $?"
echo

echo "=== materialised by the hook ==="
git -C "$REPO" ls-files --others --ignored --exclude-standard --directory \
  | while read -r p; do
      if [ -e "$TREE/$p" ]; then echo "  + $p"; else echo "    (absent) $p"; fi
    done
echo

# A second run is what Orca does after a re-run or a resumed worktree. It should
# be quiet and fast; loud output here means something is not idempotent.
echo "=== run 2 (idempotency — should be quiet) ==="
run_hook && echo "--- exit 0" || echo "--- EXIT $?"
echo
echo "Cleaning up. Check above that: run 1 exited 0, everything you expected"
echo "was materialised, and run 2 did not redo the work."
