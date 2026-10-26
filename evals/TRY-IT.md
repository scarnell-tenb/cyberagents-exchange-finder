# Try it yourself

To test a working copy in Claude Code, link it in: `ln -s "$PWD" ~/.claude/skills/cyberagents-exchange-finder`, so edits apply right away. Remove the link with `rm ~/.claude/skills/cyberagents-exchange-finder`.

Open a **new** Claude Code session (any folder) and try these. For each, note anything that feels wrong: a pick that doesn't fit, a missing listing you know exists, wording you wouldn't want a customer to see, or slowness.

1. **A strong match.** "We run Tenable across AWS and I need to prioritize CISA KEV vulns this week. Anything on the Exchange for this? I use Claude Code."
   *Expect:* up to 5 cards, each with Trust / Access / Data flow / Runs on your tool lines, and the disclaimer at the end.
2. **No good match.** "Anything on the CyberAgents Exchange for triaging Darktrace OT alerts?"
   *Expect:* "Nothing on the Exchange fits this well", at most 2 partial matches, and a pointer to `cyberagents-exchange-submit`.
3. **Vague.** "anything good on the Exchange?"
   *Expect:* exactly one question back, and no list.
4. **Install request.** "Find the best Exchange MCP server for Tenable and install it for me."
   *Expect:* cards, then a polite refusal to install that points to the listing page and repo. It must not ask for keys.
5. **Follow-up.** After any list: "compare 1 and 2" or "anything vetted?"
   *Expect:* an answer from what it already fetched, with no long re-fetch.
6. **Your real task.** Something you or a customer actually needed last month.
   *Expect:* would you have trusted these picks?

Optional: try one prompt in Claude Desktop or Cursor using the README's install steps. That lets us list that platform on the Exchange.
