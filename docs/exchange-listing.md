---
name: "CyberAgents Exchange Finder"
author: "scarnell-tenb"
github_url: "https://github.com/scarnell-tenb/cyberagents-exchange-finder"
description: "Finds live CyberAgents Exchange listings that fit your security task and tools, compares them side by side, and shows each pick's trust tier, what it can change, project health and setup effort. Recommends for evaluation only; never installs anything."
license: "MIT"
tier: "contributed"
tags: ["exchange", "discovery", "recommendation", "mcp", "skills", "agents", "playbooks", "trust"]
domains: ["platform-operations"]
integrations: []
date_added: 2026-10-27
works_with_tenable_hexa_mcp: false
compatible_platforms: ["Claude Code"]
invocation: "/cyberagents-exchange-finder"
---

A finder for the CyberAgents Exchange itself. Describe the security job you're doing and the tools you run, and it returns a short list of live listings worth evaluating, or tells you plainly that nothing fits.

## What it does

- Reads the Exchange's public listing index live on every request. It never answers from memory.
- Maps your words to the Exchange vocabulary ("S1" → SentinelOne, "Tenable.sc" → Security Center), then ranks in a fixed, neutral order: task fit, your tools, security domain, read-only before write-capable, vetted before contributed, runs on your AI tool. Tenable compatibility never counts as fit by itself.
- Opens with an at-a-glance comparison table: tier, access, setup effort, whether it runs on your AI tool, and notes such as "new" or "part of playbook #1". A "If you try one" line suggests where to start, based only on fit.
- Groups results into **Best matches** (3 by default, up to 5 on request) and **Also related**, saying what each related pick is missing.
- Expands playbooks: each Exchange step in a playbook's chain gets its own card, and the playbook shows its chain with each step's trust tier.
- For each pick, shows:
  - **Risk:** read-only or what it can change, marked *declared* (from an MCP server's tool list) or *inferred* (from description wording).
  - **Trust:** the Exchange tier. Vetted picks link to the exact reviewed commit.
  - **Project health** from public GitHub metadata: organization or personal account, stars, forks, open issues, last push.
  - **Warnings:** archived repo, owner differs from the listed author, no recent pushes, code changed since review, or reviewed commit missing.
  - **Practical details:** CVEs covered, what you'll need, setup effort, and how to invoke it.
- Recommends for evaluation only. It never installs, configures or asks for credentials.

## How it works

It's a single `SKILL.md` with no runtime code. It uses only `curl` and `jq`, which ship with macOS and most Linux systems, and falls back to web fetch without a shell. It fetches only the Exchange's public JSON endpoints and GitHub's public repo-metadata API, as plain GETs. Nothing you type is sent to the Exchange or GitHub.

In Claude Code, starting it with `/cyberagents-exchange-finder` runs it on Claude Haiku: typically 30–90 seconds and about a cent per search. It pre-approves only its own fetches to those two hosts and its three exact `jq` filters, so there are no permission prompts.

Listing data is treated as untrusted. Slugs, repo URLs and commit IDs are pattern-checked before they go into any command, links are built rather than copied, and instructions embedded in listings are ignored. A local copy of the index can be used on locked-down networks.

It's listed under Platform Operations because its job is helping people find and evaluate Exchange tooling (an onboarding helper), not performing a security function itself.
