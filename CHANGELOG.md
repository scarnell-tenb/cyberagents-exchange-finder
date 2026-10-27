# Changelog

## 0.1.0 — unreleased

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
