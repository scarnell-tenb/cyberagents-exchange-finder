# CyberAgents Exchange Finder

A skill for AI coding assistants that finds **live** [CyberAgents Exchange](https://exchange.tenable.com) listings (agents, skills, MCP servers and playbooks) that fit the security task you're working on and the tools you run. It returns a short, ranked list of listings **to evaluate**, with each one's trust tier, what it can change, where its data goes, and whether it runs on your AI tool.

It never installs anything. You decide what to try, and the listing's own repo tells you how to set it up.

## What it does

You say something like:

> We run Tenable across AWS and I need to prioritize CISA KEV vulnerabilities this week. Anything on the Exchange for this? I use Claude Code.

The skill:

1. Reads the Exchange's public listing index (`/api/listings.json`), live every time.
2. Matches your task and tools to listings using the Exchange's own vocabulary (it knows "S1" means SentinelOne and "Tenable.sc" means Security Center).
3. Ranks them in a fixed order: task fit → your tools → security domain → read-only before write-capable → vetted before contributed → runs on your AI tool. Tenable compatibility never counts as fit by itself.
4. Confirms every pick against its full Exchange record, so no listing is invented or remembered.
5. Checks each pick's GitHub repo metadata: archived? owner matches the listed author? pushed to in the last year? For vetted listings, has the code changed since the reviewed commit?
6. Shows up to 5 cards. If nothing really fits, it says so.

## Prerequisites

- Claude Code (see Install).
- Network access to `exchange.tenable.com` and `api.github.com`, **or** a local copy of the Exchange index (see "Locked-down networks").
- A shell with `curl` and `jq` is recommended. Both come with macOS 15+ and most Linux systems, so there's nothing to install. Claude Code asks once for permission to run each. Without them, the skill falls back to your tool's web fetch, which is slower.

## Install

The skill is a single file, `SKILL.md`.

### Claude Code

```bash
git clone https://github.com/scarnell-tenb/cyberagents-exchange-finder ~/.claude/skills/cyberagents-exchange-finder
```

Restart Claude Code. Invoke it with `/cyberagents-exchange-finder`, or just ask "what's on the Exchange for …".

### Claude Desktop, claude.ai and Cowork (preview: being verified)

These run skills in Anthropic's code-execution sandbox, so the skill fetches the Exchange from there, not from your machine.

1. Make sure code execution is enabled. On Team and Enterprise plans, an admin must also enable Skills.
2. Download this repo (**Code → Download ZIP**), unzip it, rename the folder to exactly `cyberagents-exchange-finder`, and zip that folder again. The folder name must match the skill name.
3. In Claude, open **Customize → Skills → + → Create skill → Upload a skill**, and upload the ZIP.
4. If your organization restricts code-execution network access, allow `exchange.tenable.com` and `api.github.com`.
5. Ask "what's on the CyberAgents Exchange for …".

Without `jq` or a shell, the skill uses whatever JSON tools are already in the sandbox, or web fetch, and its **Checks:** line says when a fallback might have missed a listing.

### Other AI tools

Version 0.1.0 is fully tested on Claude Code. The Claude apps above are in preview. `SKILL.md` follows the open Agent Skills format with plain instructions and no Claude-specific tools, so other assistants that load Agent Skills and can fetch URLs may work. They haven't been tested yet, and the Exchange listing declares Claude Code only. If you try it elsewhere, please open an issue with what happened.

## How to use

- `/cyberagents-exchange-finder`, or plain language: "find me an MCP server for SentinelOne", "is there anything on the Exchange for KEV prioritization in Tenable?"
- Mention your tools and your AI tool for better results. If your request is too vague, it asks one question.
- **Fastest:** start with `/cyberagents-exchange-finder …`. In Claude Code that runs the skill on Claude Haiku: typically 30–55 seconds and about a cent per search. When the skill triggers from plain language, it runs on your session's model instead, which is slower (about 80 seconds) but equally accurate.
- **No permission prompts:** the skill pre-approves only its own fetches to `exchange.tenable.com` and `api.github.com`, plus the three exact `jq` filters it uses. Nothing else is approved.
- Follow-ups such as "compare 1 and 3" or "anything vetted?" reuse what it already fetched.

## What it outputs

The answer opens with a one-line restatement of your need and an **at a glance** comparison table (type, tier, access, setup effort, whether it runs on your tool, notes such as "new" or "part of #2"). Then come:

- **Best matches:** up to 3 cards (say *more* for up to 5), for picks that fit your task and your tools.
- **Also related:** up to 2 cards for picks that cover only part of your need, each saying what's missing.

Example card:

```
1. **Tenable SC Reporting Assistant** — skill · [listing](https://exchange.tenable.com/skills/tenable-sc-reporting-assistant?utm_source=exchange-finder&utm_medium=skill) · [repo](https://github.com/hamzhk15/tenable-sc-reporting-assistant)
   - Does: Generates and uploads Tenable SC dashboards, PDF reports, and CSV exports via tested XML builders
   - Fits you: builds the Tenable.sc compliance dashboards you asked for
   - Risk: may change systems (inferred): description says "uploads"; confirm in the repo · talks to Tenable
   - Trust: contributed · last reviewed 3 months ago
   - Project: personal account · 6 stars · 0 forks · 0 open issues · pushed 3 months ago
   - You'll need: Tenable
   - Setup: effort low · runs on your tool ✓ · runs as instructions only · invoke `/tenable-sc-reporting-assistant`
```

A **⚠ Watch** line appears only when there's something to flag: `repo archived`, `repo owner X ≠ listed author Y`, `no pushes in 12+ months`, `no code detected in repo` (agents and MCP servers), `code has changed since review (N commits ahead)`, `reviewed commit not found in repo`, `repo not found`, `repo status unknown`, suspicious listing text, or a listing `url` that points somewhere other than the Exchange.

Every answer ends with: *"Community-built listings, presented for evaluation, not endorsement. Review the code and permissions before using in production."*

## Network and data

Every outbound request the skill makes:

| Destination | Why | What's sent |
|---|---|---|
| `https://exchange.tenable.com/api/listings.json` | listing index | plain GET, no parameters |
| `https://exchange.tenable.com/api/<type>/<slug>.json` | each pick's full record | plain GET, no parameters |
| `https://exchange.tenable.com/llms-full.txt` | vocabulary lookup, only for an unrecognized term | plain GET, no parameters |
| `https://api.github.com/repos/<owner>/<repo>` | archived / owner / last-push / project-health check, for best matches and vetted picks only | plain GET, unauthenticated. If your GitHub CLI is already signed in, the skill uses read-only `gh repo view` instead, with your own token, which goes only to GitHub |
| `https://api.github.com/repos/<owner>/<repo>/compare/<sha>...HEAD` | vetted listings only: has the code changed since review | plain GET, unauthenticated |

- **This skill sends nothing you type to the Exchange or GitHub.** None of the URLs contain your task, tools or environment. (Your conversation still goes to whichever AI provider your assistant uses, as usual.)
- **Link tagging:** links to Exchange listing pages carry a fixed `?utm_source=exchange-finder&utm_medium=skill` so the Exchange can count visits that came from this skill. It's the same for everyone and contains nothing about you or your query. GitHub links aren't tagged.
- **No telemetry, no storage.** The only file written is a scratch copy of the public index in your system temp directory, used for parsing.
- **Safety:** values from listing data (`json_url`, `github_url`, `vetted_commit_sha`) are pattern-checked before they go into any command. Listing page links are built from the listing's type and slug rather than copied. Listing text and GitHub responses are treated as untrusted data, never as instructions.

### Locked-down networks

Give the skill a local copy: download `https://exchange.tenable.com/api/listings.json` (and, optionally, detail records into `<folder>/<type>/<slug>.json`) on a connected machine, then say "use the local Exchange index at <path>". Results are labeled as coming from your local copy, and repo checks are skipped unless you say the network is available.

## Known limitations

- It depends on the Exchange's live data. If `exchange.tenable.com` is unreachable or blocked, the skill says so and stops; it never answers from memory.
- **GitHub's limit:** about 60 unauthenticated requests an hour, shared by everyone on the same network. A search uses about 3–5 of them, because only the best matches and vetted picks are checked. Searches never wait: if the limit is hit, they still answer, and the repo-health details show `repo status unknown`. If you have the GitHub CLI (`gh`) signed in, repo checks use your own 5,000-an-hour limit instead. Nothing needs installing either way.
- The **Access** line is inferred from listing metadata: MCP tool names and descriptions, and for other types the description. It's a starting point for your review, not a guarantee.
- Agents and playbooks don't declare which AI tools they support, so their cards say "not stated by listing — check the repo".
- It reads listing metadata only, never repository code. The Exchange tier tells you how far a listing has been reviewed: *contributed* = baseline review, *vetted* = security review of one specific commit.

## Development

`evals/` holds the scenario evals (`scenarios.md`), the no-skill baseline (`BASELINE.md`), results (`RESULTS.md`), fixtures, and `run.sh` / `triggers.sh` / `check_picks.py` for running and checking them with Claude Code. These are development tools only, not part of the skill. They make their own outbound calls: `check_picks.py` fetches the live listing index, and `run.sh` / `triggers.sh` run `claude -p`, which sends the eval prompts to Anthropic.

## License

MIT, see [LICENSE](LICENSE).
