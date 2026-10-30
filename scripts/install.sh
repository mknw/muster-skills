#!/usr/bin/env bash
# Link every skill in this repository into each agent skill directory on the
# machine, so every agent reads the same set. Idempotent: a re-run links new
# skills, repoints moved links, and prunes links into this repository whose
# target is no longer a skill (a renamed or deleted skill). An existing entry
# that is not a link is left alone and reported.
set -euo pipefail

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)

# One target per line: "<skill dir>|<agent dirs, any of which means present>".
# ~/.agents/skills is the Agent Skills standard's user directory; Codex and pi
# both read it, so it is linked once rather than into each agent's own dir
# (pi would otherwise load every skill twice, and ~/.codex/skills holds
# Codex's own system skills).
targets="$HOME/.claude/skills|$HOME/.claude
$HOME/.agents/skills|$HOME/.agents $HOME/.codex $HOME/.pi"

# Extra directories, colon-separated, linked whether or not an agent is found.
if [ -n "${MUSTER_SKILL_DIRS:-}" ]; then
  IFS=: read -r -a extra <<< "$MUSTER_SKILL_DIRS"
  for d in "${extra[@]}"; do targets="$targets
$d|$d"; done
fi

skills=()
for f in "$repo"/*/SKILL.md; do skills+=("$(basename "$(dirname "$f")")"); done

while IFS='|' read -r dir markers; do
  present=
  for m in $markers; do [ -d "$m" ] && present=1; done
  if [ -z "$present" ] && [ "$dir" != "$markers" ]; then
    echo "skip $dir: no agent found ($markers)"
    continue
  fi
  mkdir -p "$dir"
  linked=0 kept=0 pruned=0 alone=0
  for name in "${skills[@]}"; do
    link="$dir/$name" want="$repo/$name"
    if [ -L "$link" ]; then
      have=$(readlink "$link"); have=${have%/}
      if [ "$have" = "$want" ]; then kept=$((kept + 1)); continue; fi
      ln -sfn "$want" "$link"; echo "repointed $link (was $have)"; linked=$((linked + 1))
    elif [ -e "$link" ]; then
      echo "left alone $link: not a link"; alone=$((alone + 1))
    else
      ln -s "$want" "$link"; echo "linked $link"; linked=$((linked + 1))
    fi
  done
  for link in "$dir"/*; do
    [ -L "$link" ] || continue
    have=$(readlink "$link"); have=${have%/}
    case "$have" in "$repo"/*) ;; *) continue ;; esac
    if [ ! -f "$have/SKILL.md" ]; then rm "$link"; echo "pruned $link (was $have)"; pruned=$((pruned + 1)); fi
  done
  echo "$dir: $linked linked, $kept already linked, $pruned pruned, $alone left alone"
done <<< "$targets"
