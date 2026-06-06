#!/usr/bin/env python3
from __future__ import annotations

import re
import os
from pathlib import Path

from guard_common import ROOT, Guard, extract_backtick_values, markdown_files

CONTRACT_TOKEN = re.compile(
    r"^(?:/api/v\d+|/[a-zA-Z0-9_{}./-]+|[a-z]+:[a-z]+|[a-z]+(?:\.[a-z_]+)+|[A-Z][A-Za-z0-9]+|NAIRI_[A-Z0-9_]+|[a-z_]+\([^)]*\)|[a-z]+_[a-z0-9_]+)$"
)


def contract_values(text: str) -> set[str]:
    values = set()
    for value in extract_backtick_values(text):
        if CONTRACT_TOKEN.match(value):
            values.add(value)
    return values


def compare_pair(guard: Guard, english: Path, chinese: Path) -> None:
    en_values = contract_values(english.read_text(encoding="utf-8"))
    cn_values = contract_values(chinese.read_text(encoding="utf-8"))
    missing_cn = sorted(en_values - cn_values)
    missing_en = sorted(cn_values - en_values)
    if missing_cn:
        guard.fail(f"Chinese pair missing contract tokens for {english.relative_to(ROOT)}: {', '.join(missing_cn[:20])}")
    if missing_en:
        guard.fail(f"English pair missing contract tokens for {chinese.relative_to(ROOT)}: {', '.join(missing_en[:20])}")


def main() -> None:
    guard = Guard("i18n_doc_guard", [])
    ci_run = os.environ.get("GITHUB_ACTIONS") == "true"

    for base in ["docs", "memory-bank"]:
        if base == "memory-bank" and ci_run:
            continue
        for english in markdown_files(base):
            if english.name.endswith("-cn.md"):
                continue
            chinese = english.with_name(f"{english.stem}-cn.md")
            guard.require(chinese.exists(), f"missing bilingual pair: {chinese.relative_to(ROOT)}")
            if chinese.exists():
                compare_pair(guard, english, chinese)

    guard.finish()


if __name__ == "__main__":
    main()
