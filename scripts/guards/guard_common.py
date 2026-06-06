#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

@dataclass
class Guard:
    name: str
    errors: list[str]

    def fail(self, message: str) -> None:
        self.errors.append(message)

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.fail(message)

    def finish(self) -> None:
        if self.errors:
            print(f"{self.name}: FAILED")
            for error in self.errors:
                print(f"- {error}")
            raise SystemExit(1)
        print(f"{self.name}: ok")


def read(path: str | Path) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def exists(path: str | Path) -> bool:
    return (ROOT / path).exists()


def markdown_files(base: str | Path) -> list[Path]:
    directory = ROOT / base
    if not directory.exists():
        return []
    return sorted(directory.rglob("*.md"))


def code_fenced_spans(text: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    for match in re.finditer(r"```.*?```", text, re.DOTALL):
        spans.append(match.span())
    return spans


def in_spans(index: int, spans: list[tuple[int, int]]) -> bool:
    return any(start <= index < end for start, end in spans)


def git_check_ignored(path: str) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", "-q", path],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def git_tracked_or_untracked_nonignored() -> set[str]:
    tracked = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, text=True, capture_output=True, check=True
    ).stdout.splitlines()
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.splitlines()
    return set(tracked + untracked)


def extract_backtick_values(text: str) -> list[str]:
    return re.findall(r"`([^`]+)`", text)
