# CyberAgents Exchange Finder

A skill for AI coding assistants that finds **live** [CyberAgents Exchange](https://exchange.tenable.com) listings (agents, skills, MCP servers and playbooks) that fit the security task you're working on and the tools you run. It returns a short, ranked list of listings **to evaluate**, with each one's trust tier, what it can change, where its data goes, and whether it runs on your AI tool.

It never installs anything. You decide what to try, and the listing's own repo tells you how to set it up.

## What it does

You say something like:

> We run Tenable across AWS and I need to prioritize CISA KEV vulnerabilities this week. Anything on the Exchange for this? I use Claude Code.

The skill:

1. Reads the Exchange's public listing index (the `/api/index.json` manifest and the per-type files it lists), live every time.
2. Matches your task and tools to listings using the Exchange's own vocabulary (it knows "S1" means SentinelOne and "Tenable.sc" means Security Center).
3. Ranks them in a fixed order: task fit → your tools → security domain → read-only before write-capable → vetted before contributed → runs on your AI tool. Tenable compatibility never counts as fit by itself.
4. Confirms every pick against its full Exchange record, so no listing is invented or remembered.
5. Reads each pick's repo health from the Exchange's own snapshot (no GitHub calls): archived? owner matches the listed author? pushed to in the last year? For vetted listings, has the code changed since the reviewed commit? It checks GitHub directly only when a listing has no snapshot.
6. Shows up to 5 cards. If nothing really fits, it says so.

## Prerequisites

- Claude Code, **or** Claude Desktop / claude.ai / Cowork on a plan with Skills and code execution turned on (Settings → Capabilities). See Install.
- Network access to `exchange.tenable.com` (plus `api.github.com` for the rare repo-check fallback), **or** a local copy of the Exchange index (see "Locked-down networks").
- A shell with `curl` and `jq` is recommended. Both come with macOS 15+ and most Linux systems, so there's nothing to install. Claude Code asks once for permission to run each. Without them, the skill falls back to your tool's web fetch, which is slower.

## Install

The skill is a single file, `SKILL.md`.

### Claude Code

```bash
git clone https://github.com/scarnell-tenb/cyberagents-exchange-finder ~/.claude/skills/cyberagents-exchange-finder
```

Restart Claude Code. Invoke it with `/cyberagents-exchange-finder`, or just ask "what's on the Exchange for …".

### Claude Desktop, claude.ai and Cowork

These apps run skills in Anthropic's code-execution sandbox, so the skill fetches the Exchange from there, not from your machine.

1. Make sure code execution is on (**Settings → Capabilities**). On Team and Enterprise plans, an owner may also need to enable Skills.
2. Download [`dist/cyberagents-exchange-finder.zip`](dist/cyberagents-exchange-finder.zip): open it on GitHub, then choose **Download raw file**. A GitHub Action rebuilds it on every change to `main`, so it always matches this repo.
3. In Claude, open **Customize → Skills → + → Upload a skill** (some builds put this under **Settings → Capabilities → Skills**) and select the zip. Skills are shared with Cowork, so one upload covers both.
4. Make sure **cyberagents-exchange-finder** is toggled on.
5. If your organization restricts code-execution network access, allow `exchange.tenable.com`. Allow `api.github.com` too only if you want repo checks for the rare listing that has no Exchange health data.
6. In a new chat, ask "what's on the CyberAgents Exchange for …".

To update, remove the skill and upload the new zip. The zip's `VERSION` file tells you which version you have.

Without `jq` or a shell, the skill uses whatever JSON tools are already in the sandbox, or web fetch, and its **Checks:** line says when a fallback might have missed a listing.

The zip's `SKILL.md` is the repo file minus one frontmatter line, `model: haiku`. Only Claude Code reads it, and the apps' upload accepts only the open Agent Skills fields.

### Other AI tools

Version 0.1.0 supports Claude Code, Claude Desktop and Claude Cowork, which is what the Exchange listing declares. The automated eval suite runs on Claude Code. The Claude apps load the same `SKILL.md` through their code-execution sandbox, including the no-shell fallback that the evals cover. `SKILL.md` follows the open Agent Skills format with plain instructions and no Claude-specific tools, so other assistants that load Agent Skills and can fetch URLs may work, but they haven't been tested. If you try it elsewhere, please open an issue with what happened.

## How to use

- `/cyberagents-exchange-finder`, or plain language: "find me an MCP server for SentinelOne", "is there anything on the Exchange for KEV prioritization in Tenable?"
- Mention your tools and your AI tool for better results. If your request is too vague, it asks one question.
- **Recommended:** start with `/cyberagents-exchange-finder …`. In Claude Code that runs the skill on Claude Haiku: typically 45–95 seconds and 1–2 cents per search, and it keeps to the answer format most reliably. When the skill triggers from plain language, it runs on your session's model instead: picks are just as accurate, but it takes about 2–3 minutes, costs about 50 cents, and now and then opens with a status sentence before the answer.
- **Few permission prompts:** the skill pre-approves `curl` commands that start with an Exchange or GitHub API URL, plus the exact `jq` filters it uses, read-only `gh auth status` and `gh repo view`, and web fetch for those two domains. Claude Code asks before running anything else.
- Follow-ups such as "compare 1 and 3" or "anything vetted?" reuse what it already fetched.

## What it outputs

The answer opens with a one-line restatement of your need and an **at a glance** comparison table (type, tier, access, setup effort, whether it runs on your tool, notes such as "new" or "part of #2"). Then come:

- **Best matches:** up to 3 cards (say *more* for up to 5), for picks that fit your task and your tools.
- **Also related:** up to 2 one-line picks that cover only part of your need, each saying what's missing. Say *details N* for a full card.

Example card (live values, 2026-11-06):

```
1. **Remediation Priority & Impact Agent** — skill · [listing](https://exchange.tenable.com/skills/remediation-priority-impact-agent?utm_source=exchange-finder&utm_medium=skill)
   - Does: Prioritizes daily vulnerability fixes using Tenable exposure data, CISA KEV exploitation, MITRE ATT&CK and attack paths
   - Fits you: runs on Hexa AI MCP and turns your Tenable data into a daily fix list
   - Risk: read-only (inferred): description says it prioritizes, with no write actions · talks to Tenable, Tenable Hexa AI MCP
   - Trust: security review of commit 536616f (2026-09-23), that commit only
   - Project: personal account · 8 stars · 0 forks · 0 open issues · pushed 2 months ago · listing reviewed 1 month ago · MIT license · health as of 2026-11-05
   - Setup: needs Tenable, Tenable Hexa AI MCP · runs as instructions only · invoke `/fix-today`
```

The only links in an answer go to listing pages on the Exchange. Each listing page links to the author's repo and setup steps.

A **⚠ Watch** line appears only when there's something to flag: `repo archived`, `repo owner X ≠ listed author Y`, `no pushes in 12+ months`, `no code detected in repo` (agents and MCP servers), `code has changed since review (N commits ahead)`, `reviewed commit not found in repo`, `repo not found`, `repo status unknown`, suspicious listing text, or a listing `url` that points somewhere other than the Exchange.

Every answer ends with: *"Community-built listings, presented for evaluation, not endorsement. Review the code and permissions before using in production."*

## Network and data

Every outbound request the skill makes:

| Destination | Why | What's sent |
|---|---|---|
| `https://exchange.tenable.com/api/index.json` | manifest: which index files exist | plain GET, no parameters |
| `https://exchange.tenable.com/api/<type>.jsonl` (e.g. `skills.jsonl`, `skills-2.jsonl`) | listing index, one listing per line, one file per type | plain GET, no parameters |
| `https://exchange.tenable.com/api/<type>/<slug>.json` | each pick's full record, including the Exchange's repo-health snapshot | plain GET, no parameters |
| `https://exchange.tenable.com/llms-full.txt` | vocabulary lookup, only for an unrecognized term | plain GET, no parameters |
| `https://api.github.com/repos/<owner>/<repo>` | fallback only: when the Exchange has no repo-health data for a pick | plain GET, unauthenticated, or read-only `gh repo view` if your GitHub CLI is signed in |
| `https://api.github.com/repos/<owner>/<repo>/compare/<sha>...HEAD` | fallback only: vetted-drift check when the Exchange has no health data | plain GET, unauthenticated |

- **This skill sends nothing you type to the Exchange or GitHub.** None of the URLs contain your task, tools or environment. (Your conversation still goes to whichever AI provider your assistant uses, as usual.)
- **Link tagging:** links to Exchange listing pages carry a fixed `?utm_source=exchange-finder&utm_medium=skill` so the Exchange can count visits that came from this skill. It's the same for everyone and contains nothing about you or your query. GitHub links aren't tagged.
- **No telemetry, no storage.** The only file written is a scratch copy of the public index in your system temp directory, used for parsing.
- **Safety:** values from listing data (`json_url`, `github_url`, `vetted_commit_sha`) are pattern-checked before they go into any command. Listing page links are built from the listing's type and slug rather than copied. Listing text and GitHub responses are treated as untrusted data, never as instructions.

### Locked-down networks

Give the skill a local copy: download the files listed in `https://exchange.tenable.com/api/index.json` (and, optionally, detail records into `<folder>/<type>/<slug>.json`) on a connected machine, then say "use the local Exchange index at <path>". Results are labeled as coming from your local copy, and repo checks are skipped unless you say the network is available.

## Maintaining this repo

- **The Claude apps zip is built, not edited.** `python3 scripts/build_release.py` writes `dist/cyberagents-exchange-finder.zip` reproducibly, and `--check` verifies the committed zip matches the sources. It also fails if `VERSION` and `SKILL.md`'s `metadata.version` differ.
- **GitHub Actions keep it current:**
  - `skill-zip.yml` runs the checker tests on every pull request and push. It fails a pull request whose zip is stale, warns when `SKILL.md` changes without a `VERSION` bump, and on `main` rebuilds and commits the zip itself.
  - `secret-scan.yml` runs gitleaks on every push.
- **Local hook (optional):** `git config core.hooksPath .githooks` rebuilds and stages the zip whenever a commit touches `SKILL.md`, `README.md`, `LICENSE` or `VERSION`.
- **Releasing:** bump `VERSION` and `metadata.version` together, add a `CHANGELOG.md` entry, then tag (`git tag v0.1.0`).

## Known limitations

- **Claude Desktop and Cowork** speed and cost depend on the model you've chosen there. The `model: haiku` shortcut applies in Claude Code only.
- It depends on the Exchange's live data. If `exchange.tenable.com` is unreachable or blocked, the skill says so and stops; it never answers from memory.
- **Repo health comes from the Exchange,** which refreshes it whenever the site rebuilds. Cards show "health as of <date>". The skill calls GitHub only for a pick the Exchange has no health data for, which is rare.
- The **Access** line is inferred from listing metadata: MCP tool names and descriptions, and for other types the description. It's a starting point for your review, not a guarantee.
- Agents and playbooks don't declare which AI tools they support, so their cards say "not stated by listing — check the repo".
- It reads listing metadata only, never repository code. The Exchange tier tells you how far a listing has been reviewed: *contributed* = baseline review, *vetted* = security review of one specific commit.

## Development

`evals/` holds the scenario evals (`scenarios.md`), the no-skill baseline (`BASELINE.md`), results (`RESULTS.md`), fixtures, and `run.sh` / `triggers.sh` / `check_picks.py` for running and checking them with Claude Code. These are development tools only, not part of the skill. They make their own outbound calls: `check_picks.py` fetches the live listing index, and `run.sh` / `triggers.sh` run `claude -p`, which sends the eval prompts to Anthropic.

## License

MIT, see [LICENSE](LICENSE).
