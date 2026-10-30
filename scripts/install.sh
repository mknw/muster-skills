#!/usr/bin/env bash
# Link every skill in this repository into each agent skill directory on the
# machine, so every agent reads the same set. Idempotent. A link is only ever
# created where nothing is, or repointed when it is dead; a working link that
# points anywhere else, and any entry that is not a link, is left alone and
# reported. Links into this repository whose skill was renamed or removed are
# pruned.
set -euo pipefail
unset CDPATH   # an exported CDPATH makes `cd` print, corrupting $repo

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)

# A linked worktree is deleted sooner or later, and every link made from it
# would die with it; the main checkout is the one agents should point at.
if [ -f "$repo/.git" ] && [ -z "${MUSTER_ALLOW_WORKTREE:-}" ]; then
  echo "refusing: $repo is a linked worktree; run the main checkout's scripts/install.sh" >&2
  exit 1
fi

skills=()
for f in "$repo"/*/SKILL.md; do
  [ -f "$f" ] && skills+=("$(basename "$(dirname "$f")")")
done
if [ ${#skills[@]} -eq 0 ]; then echo "no skills found under $repo" >&2; exit 1; fi

link_into() {
  local dir=$1 name link want have real
  local linked=0 repointed=0 kept=0 pruned=0 alone=0
  if [ -L "$dir" ] && [ ! -e "$dir" ]; then echo "skip $dir: a dead link" >&2; return; fi
  mkdir -p "$dir"
  for name in "${skills[@]}"; do
    link="$dir/$name" want="$repo/$name"
    if [ -L "$link" ] && [ -e "$link" ]; then
      real=$(cd "$link" 2>/dev/null && pwd -P || true)
      if [ "$real" = "$want" ]; then kept=$((kept + 1))
      else echo "left alone $link: points at $(readlink "$link")"; alone=$((alone + 1)); fi
    elif [ -L "$link" ]; then
      echo "repointed $link (was $(readlink "$link"), dead)"; ln -sfn "$want" "$link"; repointed=$((repointed + 1))
    elif [ -e "$link" ]; then
      echo "left alone $link: not a link"; alone=$((alone + 1))
    else
      ln -s "$want" "$link"; echo "linked $link"; linked=$((linked + 1))
    fi
  done
  for link in "$dir"/*; do
    [ -L "$link" ] || continue
    have=$(readlink "$link"); have=${have%/}
    # Ours: exactly one path component below the repository, no "..".
    case "$have" in "$repo"/*/* | *..* | "$repo"/.) continue ;; "$repo"/*) ;; *) continue ;; esac
    if [ ! -f "$have/SKILL.md" ]; then rm "$link"; echo "pruned $link (was $have)"; pruned=$((pruned + 1)); fi
  done
  echo "$dir: $linked linked, $repointed repointed, $kept already linked, $pruned pruned, $alone left alone"
}

# Link into a directory when any of the given agent directories exists.
target() {
  local dir=$1 marker
  shift
  for marker in "$@"; do
    if [ -n "$marker" ] && [ -d "$marker" ]; then link_into "$dir"; return; fi
  done
  echo "skip $dir: no agent found"
}

claude_home=${CLAUDE_CONFIG_DIR:-$HOME/.claude}
target "$claude_home/skills" "$claude_home"
# The Agent Skills user directory; Codex and pi both read it, so it is linked
# once rather than into each agent's own directory (pi would load every skill
# twice, and the Codex home's skills directory holds Codex's own system skills).
target "$HOME/.agents/skills" "$HOME/.agents" "${CODEX_HOME:-$HOME/.codex}" "$HOME/.pi" "${PI_CODING_AGENT_DIR:-}"

# Extra directories, colon-separated absolute paths, linked unconditionally.
if [ -n "${MUSTER_SKILL_DIRS:-}" ]; then
  IFS=: read -r -a extra <<< "$MUSTER_SKILL_DIRS"
  for d in ${extra[@]+"${extra[@]}"}; do
    real=$(cd "$d" 2>/dev/null && pwd -P || printf '%s' "$d")
    case "$real" in
      "$repo" | "$repo"/*) echo "skip $d: inside this repository" >&2; continue ;;
    esac
    case "$d" in
      /*) link_into "$d" ;;
      '') ;;
      *) echo "skip $d: MUSTER_SKILL_DIRS entries must be absolute paths" >&2 ;;
    esac
  done
fi
