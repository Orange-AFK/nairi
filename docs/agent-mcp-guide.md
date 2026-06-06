# Nairi

## Agent and MCP Guide

### Purpose

This guide will document how agents connect to Nairi through MCP and API-backed tools.

## Relationship

### API and MCP

1. FastAPI provides product capabilities.
2. OpenAPI describes canonical API behavior.
3. MCP exposes agent-friendly tools backed by documented APIs.

## Planned Tools

### Article Tools

1. `create_article_draft_from_project_summary`
2. `explain_mdx_risks`
3. `publish_article_after_review`

## Rule

MCP must not create capabilities absent from the API contract.
