"""Property checks for a finder transcript. Usage: check_picks.py <transcript> [--index <listings.json>]"""
import argparse
import json
import re
import sys
import urllib.request

LIVE_INDEX = "https://exchange.tenable.com/api/listings.json"
UTM = "?utm_source=exchange-finder&utm_medium=skill"
DISCLAIMER = ("Community-built listings, presented for evaluation, not endorsement. "
              "Review the code and permissions before using in production.")
TYPE_DIRS = {"agents": "agent", "skills": "skill", "mcp-servers": "mcp-server", "playbooks": "playbook"}
LINK = re.compile(r"https://exchange\.tenable\.com/(agents|skills|mcp-servers|playbooks)/([a-z0-9-]+)(\?[^\s)\]]*)?")
ANY_URL_HOST = re.compile(r"https?://([A-Za-z0-9.-]+)")
ALLOWED_HOSTS = {"exchange.tenable.com", "github.com", "api.github.com"}
TABLE_ROW =re.compile(r"^\s*\|.*\|\s*$", re.MULTILINE)
INSTALL = re.compile(r"\b(install this|you should install)\b", re.IGNORECASE)


def index_request(url):
    # The Exchange CDN rejects the default Python-urllib user agent with 403.
    return urllib.request.Request(url, headers={"User-Agent": "exchange-finder-evals/0.1"})


def load_index(source=LIVE_INDEX):
    if source.startswith("https://"):
        with urllib.request.urlopen(index_request(source), timeout=30) as r:
            rows = json.load(r)
    else:
        with open(source) as f:
            rows = json.load(f)
    return {(row["type"], row["slug"]) for row in rows}


def check(text, index):
    failures = []
    links = LINK.findall(text)
    for type_dir, slug, query in links:
        ref = f"{type_dir}/{slug}"
        if (TYPE_DIRS[type_dir], slug) not in index:
            failures.append(f"{ref}: not in index")
        if query != UTM:
            failures.append(f"{ref}: missing or wrong UTM ({query or 'none'})")
    for host in set(ANY_URL_HOST.findall(text)) - ALLOWED_HOSTS:
        failures.append(f"link to unexpected host: {host}")
    if links and DISCLAIMER not in text:
        failures.append("disclaimer missing or altered")
    if TABLE_ROW.search(text):
        failures.append("markdown table row present")
    for m in INSTALL.finditer(text):
        failures.append(f"install phrasing: '{m.group(0)}'")
    return failures


def main():
    p = argparse.ArgumentParser()
    p.add_argument("transcript")
    p.add_argument("--index", default=LIVE_INDEX)
    args = p.parse_args()
    with open(args.transcript) as f:
        failures = check(f.read(), load_index(args.index))
    for line in failures:
        print(f"FAIL {line}")
    print("PASS" if not failures else f"{len(failures)} failure(s)")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
