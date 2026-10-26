#!/usr/bin/env bash
# Usage: evals/run.sh <scenario-id> [--baseline]
set -euo pipefail
id="$1"; mode="${2:-}"
repo="$(cd "$(dirname "$0")/.." && pwd)"
fixtures="$repo/evals/fixtures"

block="$(awk -v id="### $id" '$0==id{f=1;next} /^### /{f=0} f' "$repo/evals/scenarios.md")"
[ -n "$block" ] || { echo "no scenario $id" >&2; exit 2; }
prompt="$(printf '%s\n' "$block" | sed -n 's/^prompt: //p')"
prompt="${prompt//\{FIXTURES\}/$fixtures}"
data="$(printf '%s\n' "$block" | sed -n 's/^data: //p')"
tools="$(printf '%s\n' "$block" | sed -n 's/^tools: //p')"
[ -n "$tools" ] || tools='Bash(curl:*) Bash(jq:*) Bash(grep:*) Read WebFetch Skill'
read -r -a tool_args <<< "$tools"

out="$repo/evals/runs/$id${mode:+-baseline}"
rm -rf "$out"; mkdir -p "$out"
# Run outside the repo so the agent can't discover SKILL.md or references by browsing.
work="$(mktemp -d "${TMPDIR:-/tmp}/finder-eval-$id.XXXXXX")"
if [ "$mode" != "--baseline" ]; then
  mkdir -p "$work/.claude/skills/cyberagents-exchange-finder"
  cp -R "$repo/SKILL.md" "$repo/references" "$work/.claude/skills/cyberagents-exchange-finder/"
fi

(cd "$work" && claude -p "$prompt" --output-format stream-json --verbose \
  --allowedTools "${tool_args[@]}" < /dev/null > "$out/run.jsonl" 2> "$out/stderr.log") || true
rm -rf "$work"
python3 -I - "$out" <<'PY'
import json, sys
out = sys.argv[1]; result = ""; calls = []
for line in open(f"{out}/run.jsonl"):
    try: ev = json.loads(line)
    except ValueError: continue
    if ev.get("type") == "result": result = ev.get("result") or ""
    msg = ev.get("message")
    for block in (msg.get("content") or []) if isinstance(msg, dict) else []:
        if isinstance(block, dict) and block.get("type") == "tool_use":
            calls.append(f"{block['name']}: {json.dumps(block.get('input'))}")
open(f"{out}/transcript.md", "w").write(result)
open(f"{out}/tools.txt", "w").write("\n".join(calls) + "\n")
PY

index_args=()
[ "$data" = "fixtures" ] && index_args=(--index "$fixtures/listings.json")
python3 -I "$repo/evals/check_picks.py" "$out/transcript.md" ${index_args[@]+"${index_args[@]}"} | tee "$out/check.txt"
