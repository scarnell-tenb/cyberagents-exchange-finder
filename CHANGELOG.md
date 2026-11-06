# Changelog

## 0.1.0 — unreleased

- **Follows the Exchange's current index layout** (2026-11-06): reads the `/api/index.json` manifest and every per-type JSONL file it lists, including later parts like `skills-2.jsonl`. The Exchange removed `listings.json` and `listings.jsonl` (website PR #182), and a stale CDN copy of `listings.json` was still being served, so before this change searches silently missed the newest listings. The skill no longer reads either old file.
- Cards show the listing's license on the Project line. Lowercase `owner_type` values from the Exchange map to organization / personal account.
- Evals: `check_picks.py` validates links against the manifest's files and supports `--expect`; scenarios can list `expect:` listings that must appear.
- **Uses the Exchange's agent-friendly API** (live since 2026-10-28): reads `listings.jsonl` and takes repo health and vetted drift from each listing's `repo` object, so a normal search makes no GitHub calls. Older deployments and listings without health data fall back to the previous GitHub checks.

First version: find and evaluate CyberAgents Exchange listings for a security task.

- **Live data only.** Reads the Exchange's public index on every request, confirms each pick against its detail record, and never answers from memory.
- **Neutral, fixed ranking.** Task fit → your tools → domain → read-only before write-capable → vetted before contributed → runs on your AI tool. Tenable compatibility never counts as fit by itself.
- **Answer layout:**
  - Need line, optional Assumed and Checks lines, and an "If you try one" line.
  - An at-a-glance comparison table with linked listing names.
  - **Best matches** (3 by default, up to 5 on request) and **Also related**.
- **Playbook chains.** Exchange steps in a playbook become their own cards. The playbook shows its chain with each step's tier, and each step card says "Part of playbook #n".
- **Practitioner signals on every card:**
  - Risk, marked declared or inferred.
  - Trust tier, with a link to the reviewed commit for vetted picks.
  - Project health: organization or personal account, stars, forks, open issues, last push.
  - Fixed setup effort (low for skills, medium for MCP servers, high for agents and playbooks).
  - CVEs covered, and freshness ("new" when added in the last 30 days).
  - What you'll need, and how to invoke it.
- **Warnings from public GitHub metadata:** archived repo, owner differs from the listed author, no pushes in 12+ months, no code detected (agents and MCP servers), code changed since review, reviewed commit missing, repo not found.
- **Safety:**
  - Finds only, never installs.
  - Listing data is untrusted: values are pattern-checked before use, links are built rather than copied, and embedded instructions are ignored.
  - Commit messages are never used to downplay a warning.
- **Privacy:** only plain GETs to `exchange.tenable.com` and `api.github.com`, and nothing the user types goes into a request. Exchange links carry a fixed `utm_source=exchange-finder` tag.
- **Claude Code:**
  - `model: haiku` applies when the skill is started with `/cyberagents-exchange-finder`.
  - `allowed-tools` pre-approves only the skill's own fetches and its three exact `jq` filters.
- **Fallbacks:** web fetch when there's no shell, and a local index copy for locked-down networks.
