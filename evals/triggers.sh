#!/usr/bin/env bash
# Usage: evals/triggers.sh  — runs evals/triggers.md prompts with the skill installed; prints FIRED/quiet per prompt.
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
out="$repo/evals/runs/triggers"; rm -rf "$out"; mkdir -p "$out"
grep -E '^- [TN][0-9]+: ' "$repo/evals/triggers.md" | while IFS= read -r line; do
  id="${line#- }"; id="${id%%:*}"; prompt="${line#*: }"
  work="$(mktemp -d "${TMPDIR:-/tmp}/finder-trig-$id.XXXXXX")"
  mkdir -p "$work/.claude/skills/cyberagents-exchange-finder"
  cp "$repo/SKILL.md" "$work/.claude/skills/cyberagents-exchange-finder/"
  (cd "$work" && claude -p "$prompt" --output-format stream-json --verbose \
     --allowedTools "Bash(curl:*)" "Bash(jq:*)" "Bash(grep:*)" "Read" "WebFetch" "Skill" < /dev/null > "$out/$id.jsonl" 2>/dev/null) || true
  rm -rf "$work"
  if grep -q -E '"skill": ?"cyberagents-exchange-finder"' "$out/$id.jsonl"; then echo "$id FIRED"; else echo "$id quiet"; fi
done
