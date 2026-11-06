"""Property checks for a finder transcript.
Usage: check_picks.py <transcript> [--index <listings.json|.jsonl>] [--expect <type-dir>/<slug> ...]"""
import argparse
import json
import re
import sys
import urllib.request

# The live index is the manifest plus every per-type JSONL file it lists.
MANIFEST = "https://exchange.tenable.com/api/index.json"
UTM = "?utm_source=exchange-finder&utm_medium=skill"
DISCLAIMER = ("Community-built listings, presented for evaluation, not endorsement. "
              "Review the code and permissions before using in production.")
TIERS = ("Tiers: contributed = baseline review only, not a comprehensive security audit "
         "· vetted = security review of one specific commit.")
TYPE_DIRS = {"agents": "agent", "skills": "skill", "mcp-servers": "mcp-server", "playbooks": "playbook"}
LINK = re.compile(r"https://exchange\.tenable\.com/(agents|skills|mcp-servers|playbooks)/([a-z0-9-]+)(\?[^\s)\]]*)?")
ANY_URL_HOST = re.compile(r"https?://([A-Za-z0-9.-]+)")
# Answers link only to Exchange listing pages, so traffic goes to the Exchange.
ALLOWED_HOSTS = {"exchange.tenable.com"}
TABLE_ROW =re.compile(r"^\s*\|.*\|\s*$", re.MULTILINE)
INSTALL = re.compile(r"\b(install this|you should install)\b", re.IGNORECASE)


def index_request(url):
    # The Exchange CDN rejects the default Python-urllib user agent with 403.
    return urllib.request.Request(url, headers={"User-Agent": "exchange-finder-evals/0.1"})


def fetch_text(url):
    with urllib.request.urlopen(index_request(url), timeout=30) as r:
        return r.read().decode("utf-8")


def parse_rows(text):
    text = text.strip()
    if text.startswith("["):
        return json.loads(text)
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def load_index(source=MANIFEST):
    if source == MANIFEST:
        manifest = json.loads(fetch_text(MANIFEST))
        rows = [row for t in manifest["types"] for f in t["files"] for row in parse_rows(fetch_text(f["url"]))]
    else:
        with open(source) as f:
            rows = parse_rows(f.read())
    return {(row["type"], row["slug"]) for row in rows}


def outside_at_a_glance(text):
    # The At a glance section runs from its heading to the next bold heading line.
    return re.sub(r"\*\*At a glance\*\*.*?(?=^\*\*[A-Z])", "", text, flags=re.S | re.M)


def check(text, index, expect=()):
    failures = []
    links = LINK.findall(text)
    shown = {f"{d}/{s}" for d, s, _ in links}
    for ref in expect:
        if ref not in shown:
            failures.append(f"expected listing not shown: {ref}")
    for type_dir, slug, query in links:
        ref = f"{type_dir}/{slug}"
        if (TYPE_DIRS[type_dir], slug) not in index:
            failures.append(f"{ref}: not in index")
        if query != UTM:
            failures.append(f"{ref}: missing or wrong UTM ({query or 'none'})")
    for host in set(ANY_URL_HOST.findall(text)) - ALLOWED_HOSTS:
        failures.append(f"link to unexpected host: {host}")
    if links and not text.lstrip().startswith("**Need:**"):
        failures.append("answer doesn't start with the **Need:** line")
    if links and TIERS not in text:
        failures.append("Tiers line missing or altered")
    if links and DISCLAIMER not in text:
        failures.append("disclaimer missing or altered")
    if TABLE_ROW.search(outside_at_a_glance(text)):
        failures.append("markdown table row outside the At a glance section")
    for m in INSTALL.finditer(text):
        failures.append(f"install phrasing: '{m.group(0)}'")
    return failures


def main():
    p = argparse.ArgumentParser()
    p.add_argument("transcript")
    p.add_argument("--index", default=MANIFEST)
    p.add_argument("--expect", nargs="*", default=[])
    args = p.parse_args()
    with open(args.transcript) as f:
        failures = check(f.read(), load_index(args.index), args.expect)
    for line in failures:
        print(f"FAIL {line}")
    print("PASS" if not failures else f"{len(failures)} failure(s)")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
