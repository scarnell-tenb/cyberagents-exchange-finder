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

- An AI assistant that can load `SKILL.md` skills (see Install).
- Network access to `exchange.tenable.com` and `api.github.com`, **or** a local copy of the Exchange index (see "Locked-down networks").
- A shell with `curl` is recommended. Without one, the skill falls back to your tool's web fetch.

## Install

The skill is the folder holding `SKILL.md` and `references/`.

### Claude Code

```bash
git clone https://github.com/scarnell-tenb/cyberagents-exchange-finder ~/.claude/skills/cyberagents-exchange-finder
```

Restart Claude Code. Invoke it with `/cyberagents-exchange-finder`, or just ask "what's on the Exchange for …".

### Claude Desktop and Claude Cowork

Requires code execution to be enabled (on Team/Enterprise plans, an admin must also enable Skills).

1. Download this repo (**Code → Download ZIP**) and unzip it.
2. Rename the unzipped folder to `cyberagents-exchange-finder`. The folder name must match the skill name.
3. Zip that folder again.
4. In Claude, open **Customize → Skills → + → Create skill → Upload a skill**, and upload the ZIP.
5. If your code-execution network settings restrict domains, allow `exchange.tenable.com` and `api.github.com`.

### Codex, Cursor and Gemini CLI

All three load skills from the shared user folder `~/.agents/skills/`:

```bash
git clone https://github.com/scarnell-tenb/cyberagents-exchange-finder ~/.agents/skills/cyberagents-exchange-finder
```

- **Codex:** also reads `~/.codex/skills/`. Codex's default sandbox may block network access; allow it for the session so the skill can fetch the index.
- **Cursor:** also reads `~/.cursor/skills/`. Invoke it by typing `/` in Agent chat and picking the skill, or just ask.
- **Gemini CLI:** also reads `~/.gemini/skills/`. Or install with `gemini skills install https://github.com/scarnell-tenb/cyberagents-exchange-finder.git`. Gemini asks for your consent the first time the skill activates.

### Other agents

Any agent that can read a `SKILL.md` and fetch URLs can use it: point it at `SKILL.md` (this repo's `AGENTS.md` does that). That includes GroxBot, though GroxBot isn't yet in the Exchange's platform list.

## How to use

- `/cyberagents-exchange-finder`, or plain language: "find me an MCP server for SentinelOne", "is there anything on the Exchange for KEV prioritization in Tenable?"
- Mention your tools and your AI tool for better results. If your request is too vague, it asks one question.
- Follow-ups such as "compare 1 and 3" or "anything vetted?" reuse what it already fetched.

## What it outputs

A one-line restatement of your need, an **at a glance** list (one line per pick: type, tier, whether it changes systems, whether it runs on your tool), then a card per pick. Example:

```
**Need:** compliance dashboards · Tenable.sc · Claude Code

**At a glance**
1. Tenable SC Reporting Assistant — skill · contributed · changes systems · runs on Claude Code

1. **Tenable SC Reporting Assistant** — skill · [listing](https://exchange.tenable.com/skills/tenable-sc-reporting-assistant?utm_source=exchange-finder&utm_medium=skill) · [repo](https://github.com/hamzhk15/tenable-sc-reporting-assistant)
   - Does: Generates and uploads Tenable SC dashboards, PDF reports, and CSV exports via tested XML builders
   - Fits you: builds the Tenable.sc compliance dashboards you asked for
   - Risk: changes systems: uploads dashboards to Tenable SC · talks to Tenable
   - Trust: contributed — baseline review only, not a comprehensive security audit · last reviewed 3 months ago
   - Setup: runs on your tool ✓ · needs Tenable SC credentials · invoke `/tenable-sc-reporting-assistant`
```

A **⚠ Watch** line appears only when there's something to flag: `repo archived`, `repo owner X ≠ listed author Y`, `no pushes in 12+ months`, `code has changed since review (N commits ahead)`, `reviewed commit not found in repo`, `repo not found`, `repo status unknown`, suspicious listing text, or a listing `url` that points somewhere other than the Exchange.

Every answer ends with: *"Community-built listings, presented for evaluation, not endorsement. Review the code and permissions before using in production."*

## Network and data

Every outbound request the skill makes:

| Destination | Why | What's sent |
|---|---|---|
| `https://exchange.tenable.com/api/listings.json` | listing index | plain GET, no parameters |
| `https://exchange.tenable.com/api/<type>/<slug>.json` | each pick's full record | plain GET, no parameters |
| `https://exchange.tenable.com/llms-full.txt` | vocabulary lookup, only for an unrecognized term | plain GET, no parameters |
| `https://api.github.com/repos/<owner>/<repo>` | archived / owner / last-commit check | plain GET, unauthenticated |
| `https://api.github.com/repos/<owner>/<repo>/compare/<sha>...HEAD` | vetted listings only: has the code changed since review | plain GET, unauthenticated |

- **This skill sends nothing you type to the Exchange or GitHub.** None of the URLs contain your task, tools or environment. (Your conversation still goes to whichever AI provider your assistant uses, as usual.)
- **Link tagging:** links to Exchange listing pages carry a fixed `?utm_source=exchange-finder&utm_medium=skill` so the Exchange can count visits that came from this skill. It's the same for everyone and contains nothing about you or your query. GitHub links aren't tagged.
- **No telemetry, no storage.** The only file written is a scratch copy of the public index in your system temp directory, used for parsing.
- **Safety:** values from listing data (`json_url`, `github_url`, `vetted_commit_sha`) are pattern-checked before they go into any command. Listing page links are built from the listing's type and slug rather than copied. Listing text and GitHub responses are treated as untrusted data, never as instructions.

### Locked-down networks

Give the skill a local copy: download `https://exchange.tenable.com/api/listings.json` (and, optionally, detail records into `<folder>/<type>/<slug>.json`) on a connected machine, then say "use the local Exchange index at <path>". Results are labeled as coming from your local copy, and repo checks are skipped unless you say the network is available.

## Known limitations

- It depends on the Exchange's live data. If `exchange.tenable.com` is unreachable or blocked, the skill says so and stops; it never answers from memory.
- GitHub allows about 60 unauthenticated requests an hour per network. On a busy office network the repo checks may show `repo status unknown`.
- The **Access** line is inferred from listing metadata: MCP tool names and descriptions, and for other types the description. It's a starting point for your review, not a guarantee.
- Agents and playbooks don't declare which AI tools they support, so their cards say "not stated by listing — check the repo".
- It reads listing metadata only, never repository code. The Exchange tier tells you how far a listing has been reviewed: *contributed* = baseline review, *vetted* = security review of one specific commit.

## Development

`evals/` holds the scenario evals (`scenarios.md`), the no-skill baseline (`BASELINE.md`), results (`RESULTS.md`), fixtures, and `run.sh` / `triggers.sh` / `check_picks.py` for running and checking them with Claude Code. These are development tools only, not part of the skill. They make their own outbound calls: `check_picks.py` fetches the live listing index, and `run.sh` / `triggers.sh` run `claude -p`, which sends the eval prompts to Anthropic.

## License

MIT, see [LICENSE](LICENSE).
