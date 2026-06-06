#!/usr/bin/env python3
from __future__ import annotations

import re

from guard_common import Guard, read

LOWER_CAMEL = re.compile(r"^[a-z][A-Za-z0-9]*$")
SNAKE_PATH_PARAM = re.compile(r"^[a-z][a-z0-9_]*$")


def split_fields(line: str) -> list[str]:
    _, raw = line.split(":", 1)
    return [item.strip().strip("`") for item in raw.split(",") if item.strip()]


def main() -> None:
    guard = Guard("api_schema_guard", [])
    api = read("memory-bank/api-contract.md")

    for match in re.finditer(r"Path:\s+`([^`]+)`", api):
        path = match.group(1)
        guard.require(path.startswith("/api/v1"), f"API path must start with /api/v1: {path}")
        for param in re.findall(r"{([^}]+)}", path):
            guard.require(SNAKE_PATH_PARAM.match(param) is not None, f"path parameter must be snake_case: {path} uses {param}")

    field_prefixes = (
        "Request body fields:", "Response fields:", "Query parameters:", "Query 参数:", "Response 字段:", "Request body 字段:",
    )
    for line_number, line in enumerate(api.splitlines(), start=1):
        stripped = line.strip()
        if not any(prefix in stripped for prefix in field_prefixes):
            continue
        for field in split_fields(stripped):
            if field in {"items", "details"}:
                continue
            guard.require(LOWER_CAMEL.match(field) is not None, f"API field should use lowerCamelCase in api-contract.md:{line_number}: {field}")

    guard.finish()


if __name__ == "__main__":
    main()
