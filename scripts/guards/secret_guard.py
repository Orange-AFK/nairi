#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

from guard_common import ROOT, Guard, git_tracked_or_untracked_nonignored

SECRET_PATTERNS = [
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |)?PRIVATE KEY-----")),
    ("github token", re.compile(r"gh[pousr]_[A-Za-z0-9_]{30,}")),
    ("generic bearer token", re.compile(r"Bearer\s+[A-Za-z0-9._~+/=-]{30,}")),
    ("cloudflare token", re.compile(r"(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])\b[A-Za-z0-9_-]{40,}\b")),
    ("aws access key", re.compile(r"AKIA[0-9A-Z]{16}")),
]

PLACEHOLDER_ALLOWLIST = [
    "change-me",
    "placeholder",
    "example",
    "your-",
    "replace-me",
    "changeme",
]

SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".ico"}


def is_placeholder_line(line: str) -> bool:
    lowered = line.lower()
    return any(token in lowered for token in PLACEHOLDER_ALLOWLIST)


def main() -> None:
    guard = Guard("secret_guard", [])
    for rel in sorted(git_tracked_or_untracked_nonignored()):
        path = ROOT / rel
        if not path.is_file() or path.suffix.lower() in SKIP_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if is_placeholder_line(line):
                continue
            for label, pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    guard.fail(f"possible {label} in {rel}:{line_number}")
            if re.search(
                r"(?i)\b(api[_-]?key|secret|token|password)\s*=\s*['\"]?[A-Za-z0-9_~+/=-]{12,}['\"]?\s*(?:#.*)?$",
                line,
            ) and not is_placeholder_line(line):
                guard.fail(f"possible secret assignment in {rel}:{line_number}")
    guard.finish()


if __name__ == "__main__":
    main()
