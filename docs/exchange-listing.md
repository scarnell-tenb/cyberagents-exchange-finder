---
name: "CyberAgents Exchange Finder"
author: "scarnell-tenb"
github_url: "https://github.com/scarnell-tenb/cyberagents-exchange-finder"
description: "Finds live CyberAgents Exchange listings that fit your security task and tools, and shows each pick's trust tier, what it can change, where its data goes, and whether it runs on your AI tool. Recommends for evaluation only; never installs anything."
license: "MIT"
tier: "contributed"
tags: ["exchange", "discovery", "recommendation", "mcp", "skills", "agents", "trust"]
domains: ["platform-operations"]
integrations: []
date_added: 2026-10-26
works_with_tenable_hexa_mcp: false
compatible_platforms: ["Claude Code"]
invocation: "/cyberagents-exchange-finder"
---

A finder for the CyberAgents Exchange itself. Describe the security job you're doing and the tools you run, and it returns up to five live listings worth evaluating, or tells you plainly that nothing fits.

## What it does

- Reads the Exchange's public listing index live on every request. It never answers from memory.
- Maps your words to the Exchange vocabulary ("S1" → SentinelOne, "Tenable.sc" → Security Center), then ranks in a fixed, neutral order: task fit, your tools, security domain, read-only before write-capable, vetted before contributed, runs on your AI tool. Tenable compatibility never counts as fit by itself.
- Confirms every pick against its full Exchange record, then checks the repo's GitHub metadata: archived, owner vs. listed author, last push, and for vetted listings whether the code has changed since the reviewed commit.
- Shows each pick as a card with its trust tier explained in the Exchange's own words, an Access line (read-only or what it can change), a data-flow line, and platform compatibility.
- Recommends for evaluation only. It never installs, configures or asks for credentials.

## How it works

It's a single `SKILL.md` plus one reference file, with no runtime code. It fetches only the Exchange's public JSON endpoints and GitHub's public repo-metadata API, as plain GETs. Nothing you type is sent to the Exchange or GitHub. Listing data is treated as untrusted: values are pattern-checked before they go into any command, and instructions embedded in listings are ignored. A local copy of the index can be used on locked-down networks.

It's listed under Platform Operations because its job is helping people find and evaluate Exchange tooling (an onboarding helper), not performing a security function itself.
