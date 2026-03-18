<p align="center">
  <img src="assets/logo.png" width="150" alt="tflow logo" />
</p>

# tflow - AI-Powered E2E Test Generation CLI

[中文](README_zh.md) | English

`tflow` is a command-line interface that uses Claude AI to automatically analyze your frontend project, detect core workflows, and generate reliable Playwright E2E tests.

## Installation

Ensure you have Python 3.11+ installed.

```bash
pip install tflow
```

Set your Anthropic API Key:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Quick Start

1. Go to your frontend project:
```bash
cd my-vue-project
```

2. Run the full pipeline (Analysis -> Plan -> Generation -> Verification):
```bash
tflow run .
```

## Commands

- `tflow run .`: Run full E2E test generation pipeline.
- `tflow plan .`: Generate a test plan for human review.
- `tflow analyze .`: Run code analysis only.
- `tflow verify .`: Run verification on existing tests.
- `tflow list`: List managed test cases.
- `tflow config`: Configuration management commands.
- `tflow tool`: External tool system commands for setting up third-party integrations (API, DB, scripts).

## Architecture

tflow uses a deterministic Python orchestrator with the `claude-agent-sdk` executing targeted structural analysis and generation tasks, saving AI costs up to 90% via MD5 source file caching and AST-based dependency mappings.

## Cross-System Integration

You can integrate APIs and database checks within your UI e2e tests by registering a tool:
```bash
tflow tool add my_api_validator
```
