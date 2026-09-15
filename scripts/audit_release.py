from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".git", ".venv", "venv", "build", "dist", "__pycache__", ".pytest_cache"}
FORBIDDEN_SUFFIXES = {".db", ".sqlite", ".sqlite3", ".log", ".key", ".pem", ".p12", ".pfx"}
FORBIDDEN_NAMES = {".env", "credentials.json", "secrets.json"}
PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "api key": re.compile(r"\b(?:sk-proj-|sk-ant-|gsk_|github_pat_|ghp_)[A-Za-z0-9_-]{12,}"),
    "personal Windows path": re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+", re.I),
}


def main() -> int:
    findings: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in SKIP_PARTS for part in path.parts):
            continue
        relative = path.relative_to(ROOT).as_posix()
        if path.name.lower() in FORBIDDEN_NAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            findings.append(f"forbidden file: {relative}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(f"unexpected binary file: {relative}")
            continue
        for label, pattern in PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{label}: {relative}")
    if findings:
        sys.stderr.write("\n".join(findings) + "\n")
        return 1
    print("release audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

