#!/usr/bin/env python3
from __future__ import annotations

import re
import os
from pathlib import Path

from guard_common import ROOT, Guard, exists, git_check_ignored, markdown_files, read


def main() -> None:
    guard = Guard("docs_guard", [])
    require_local_memory_pairs = os.environ.get("GITHUB_ACTIONS") != "true"

    for required in ["README.md", "README-cn.md", "LICENSE", "AGENTS.md", ".gitignore", ".env.example"]:
        guard.require(exists(required), f"missing required root file: {required}")

    if exists("README.md"):
        guard.require("README-cn.md" in read("README.md"), "README.md must link to README-cn.md")
    if exists("LICENSE"):
        license_text = read("LICENSE")
        guard.require("MIT License" in license_text, "LICENSE must use MIT License")

    forbidden_root_docs = {
        "progress.md", "roadmap.md", "design.md", "architecture.md",
        "requirements.md", "tech-stack.md", "api-contract.md", "data-model.md",
    }
    for name in forbidden_root_docs:
        guard.require(not exists(name), f"forbidden development document in root: {name}")

    docs_dir = ROOT / "docs"
    memory_dir = ROOT / "memory-bank"
    guard.require(docs_dir.exists(), "docs/ directory is required")
    guard.require(memory_dir.exists(), "memory-bank/ directory is required")

    for path in markdown_files("docs"):
        if path.name.endswith("-cn.md"):
            continue
        pair = path.with_name(f"{path.stem}-cn.md")
        guard.require(pair.exists(), f"docs file missing Chinese pair: {path.relative_to(ROOT)}")

    for path in markdown_files("memory-bank"):
        if path.name.endswith("-cn.md"):
            guard.require(git_check_ignored(str(path.relative_to(ROOT))), f"memory-bank Chinese file must be git-ignored: {path.relative_to(ROOT)}")
            continue
        pair = path.with_name(f"{path.stem}-cn.md")
        if require_local_memory_pairs:
            guard.require(pair.exists(), f"memory-bank file missing local Chinese pair: {path.relative_to(ROOT)}")

    root_md_files = [p.name for p in ROOT.glob("*.md")]
    allowed_root_md = {"README.md", "README-cn.md", "AGENTS.md"}
    for name in root_md_files:
        guard.require(name in allowed_root_md, f"unexpected root markdown file: {name}")

    forbidden_doc_keywords = re.compile(r"\b(progress log|roadmap|architecture decision|internal development|contract index)\b", re.I)
    for path in markdown_files("docs"):
        text = path.read_text(encoding="utf-8")
        guard.require(not forbidden_doc_keywords.search(text), f"docs/ appears to contain internal planning vocabulary: {path.relative_to(ROOT)}")

    forbidden_stage_heading = re.compile(r"^#{1,6}\s+(Step\s+\d+|Phase\s+\d+|Slice\s+\w+|步骤\s*\d+|阶段\s*\d+)", re.I | re.M)
    for path in markdown_files("."):
        rel = path.relative_to(ROOT)
        if ".git" in rel.parts:
            continue
        text = path.read_text(encoding="utf-8")
        guard.require(not forbidden_stage_heading.search(text), f"forbidden abstract stage heading in {rel}")

    guard.finish()


if __name__ == "__main__":
    main()
