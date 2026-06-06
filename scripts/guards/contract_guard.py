#!/usr/bin/env python3
from __future__ import annotations

import re
from collections import Counter

from guard_common import ROOT, Guard, extract_backtick_values, markdown_files, read

HTTP_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}


def values_from_contract_index() -> set[str]:
    return set(extract_backtick_values(read("memory-bank/contract-index.md")))


def api_contract_blocks(text: str) -> list[dict[str, str]]:
    blocks: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in text.splitlines():
        if line.startswith("### "):
            if current:
                blocks.append(current)
            current = {"title": line[4:].strip()}
            continue
        match = re.match(r"\d+\.\s+(Method|Path|Scope|Audit event):\s+`?([^`]+?)`?\s*$", line)
        if match and current is not None:
            current[match.group(1).lower().replace(" ", "_")] = match.group(2).strip()
    if current:
        blocks.append(current)
    return [block for block in blocks if "path" in block or "method" in block or "scope" in block]


def main() -> None:
    guard = Guard("contract_guard", [])
    index_values = values_from_contract_index()
    api_text = read("memory-bank/api-contract.md")
    contract_paths = []

    for block in api_contract_blocks(api_text):
        title = block.get("title", "unknown")
        method = block.get("method")
        path = block.get("path")
        scope = block.get("scope")
        if path:
            contract_paths.append(path)
            guard.require(path.startswith("/api/v1"), f"API path must start with /api/v1 in {title}: {path}")
            guard.require(method in HTTP_METHODS, f"API block missing valid Method for {title}")
            guard.require(bool(scope), f"API block missing Scope for {title}")
            if scope:
                guard.require(scope in index_values, f"API scope not registered in contract-index.md for {title}: {scope}")

    duplicate_paths = [path for path, count in Counter(contract_paths).items() if count > 1]
    for path in duplicate_paths:
        # Same path may be valid with different methods; require no exact method+path duplicates instead.
        pass

    exact_pairs = Counter((block.get("method"), block.get("path")) for block in api_contract_blocks(api_text) if block.get("path"))
    for pair, count in exact_pairs.items():
        guard.require(count == 1, f"duplicate API method/path contract: {pair[0]} {pair[1]}")

    for path in contract_paths:
        guard.require(path in read("memory-bank/integration-map.md") or "publish" not in path, f"important API path should be mapped in integration-map.md: {path}")

    agent_text = read("memory-bank/agent-mcp-design.md")
    tool_names = sorted(set(re.findall(r"Tool name:\s+`([a-z][a-z0-9_]+)`", agent_text)))
    for tool in tool_names:
        guard.require(re.match(r"^[a-z][a-z0-9_]*$", tool) is not None, f"MCP tool must use snake_case: {tool}")
        guard.require("Backed by:" in agent_text, f"MCP tool missing Backed by mapping context: {tool}")

    deployment_text = read("memory-bank/deployment.md")
    env_example = read(".env.example")
    env_in_docs = set(re.findall(r"`(NAIRI_[A-Z0-9_]+)`", deployment_text))
    env_in_example = set(re.findall(r"^(NAIRI_[A-Z0-9_]+)=", env_example, re.M))
    guard.require(env_in_docs == env_in_example, f"environment variables differ between deployment.md and .env.example: docs_only={sorted(env_in_docs-env_in_example)}, example_only={sorted(env_in_example-env_in_docs)}")

    for value in index_values:
        if value.startswith("/"):
            guard.require(value.startswith("/api/v1") or not value.startswith("/api/"), f"contract-index path uses unsupported API prefix: {value}")

    # Ensure canonical entities appear in data-model when they are model-like and planned.
    data_model = read("memory-bank/data-model.md")
    for entity in ["User", "Role", "ApiToken", "Post", "PostRevision", "MdxComponent", "PublishJob", "AgentTask", "AuditEvent"]:
        guard.require(f"### {entity}" in data_model, f"canonical entity missing from data-model.md: {entity}")

    # Ensure audit events referenced by API are registered.
    for audit in re.findall(r"Audit event:\s+`([^`]+)`", api_text):
        guard.require(audit in index_values, f"audit event not registered in contract-index.md: {audit}")

    guard.finish()


if __name__ == "__main__":
    main()
