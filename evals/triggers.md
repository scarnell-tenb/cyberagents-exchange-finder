# Trigger test

Run each prompt with the skill installed in the project (no mention of the skill by name). A pass is: should-fire prompts load the skill (the transcript shows the Exchange API being fetched, or the restated-need line), and should-not prompts don't.

## Should fire
- T1: what's on the Exchange for SentinelOne?
- T2: find me an MCP server for Splunk on the CyberAgents Exchange
- T3: is there an agent or skill out there for CISA KEV prioritization in Tenable? check the exchange
- T4: recommend some exchange.tenable.com listings for cloud posture in AWS
- T5: any playbooks on the CyberAgents Exchange for incident response?

## Should not fire
- N1: explain what EPSS is in two sentences
- N2: write a Sigma rule that detects certutil downloading files
- N3: what's the difference between Tenable.io and Tenable.sc?
- N4: summarize the CISA KEV catalog's purpose in one paragraph
- N5: how do I configure an MCP server in Claude Code?
