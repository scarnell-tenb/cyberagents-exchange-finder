#!/usr/bin/env python3
"""Build the uploadable skill zip for Claude Desktop, claude.ai and Cowork, reproducibly.

The zip's top-level folder matches the `name:` in SKILL.md, as Claude's skill upload
requires. The build is deterministic: the same sources give the same entries, with
sorted names, fixed timestamps and fixed permissions. --check compares entry names,
modes and file bytes rather than compressed bytes, so a different zlib on a CI runner
can't cause a false "stale" result.

The zip's SKILL.md drops frontmatter keys that only Claude Code reads (CLAUDE_CODE_ONLY),
because the Claude apps' upload accepts only the open Agent Skills fields. Everything
else is byte-for-byte the repo file.

Usage:
  python3 scripts/build_release.py            # write dist/<name>.zip
  python3 scripts/build_release.py --check    # exit 1 if dist/<name>.zip is missing or stale
"""
from __future__ import annotations

import argparse
import io
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INCLUDE_FILES = ["SKILL.md", "README.md", "LICENSE", "VERSION"]
CLAUDE_CODE_ONLY = ("model",)
EPOCH = (1980, 1, 1, 0, 0, 0)


def read_skill() -> str:
    return (ROOT / "SKILL.md").read_text(encoding="utf-8")


def frontmatter(text: str) -> str:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        sys.exit("SKILL.md has no frontmatter block")
    return m.group(1)


def skill_name(text: str) -> str:
    m = re.search(r"^name:\s*(\S+)\s*$", frontmatter(text), re.M)
    if not m:
        sys.exit("SKILL.md has no name: in its frontmatter")
    return m.group(1).strip("\"'")


def check_version(text: str) -> str:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    m = re.search(r"^\s+version:\s*\"?([^\"\s]+)\"?\s*$", frontmatter(text), re.M)
    if not m or m.group(1) != version:
        sys.exit(f"VERSION says {version} but SKILL.md metadata.version says "
                 f"{m.group(1) if m else 'nothing'}. Make them match.")
    return version


def app_skill_md(text: str) -> bytes:
    """SKILL.md as the Claude apps get it: Claude Code-only frontmatter keys removed."""
    fm = frontmatter(text)
    kept = "\n".join(line for line in fm.split("\n")
                     if not any(line.startswith(f"{key}:") for key in CLAUDE_CODE_ONLY))
    return text.replace(fm, kept, 1).encode("utf-8")


def build_bytes(name: str, text: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        zi = zipfile.ZipInfo(f"{name}/", EPOCH)
        zi.external_attr = (0o40755 << 16) | 0x10
        z.writestr(zi, b"")
        for rel in sorted(INCLUDE_FILES):
            data = app_skill_md(text) if rel == "SKILL.md" else (ROOT / rel).read_bytes()
            zi = zipfile.ZipInfo(f"{name}/{rel}", EPOCH)
            zi.external_attr = 0o100644 << 16
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, data)
    return buf.getvalue()


def entries(data: bytes) -> dict:
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        return {i.filename: (i.external_attr >> 16, z.read(i)) for i in z.infolist()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="fail if the committed zip doesn't match the sources")
    args = ap.parse_args()
    text = read_skill()
    name = skill_name(text)
    version = check_version(text)
    out = ROOT / "dist" / f"{name}.zip"
    data = build_bytes(name, text)
    current = out.is_file() and entries(out.read_bytes()) == entries(data)
    if args.check:
        if not current:
            print(f"STALE: {out.relative_to(ROOT)} does not match the sources. Run: python3 scripts/build_release.py")
            return 1
        print(f"OK: {out.relative_to(ROOT)} matches the sources (version {version})")
        return 0
    if current:
        print(f"{out.relative_to(ROOT)} already up to date (version {version})")
        return 0
    out.parent.mkdir(exist_ok=True)
    out.write_bytes(data)
    print(f"{out.relative_to(ROOT)} written (version {version})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
