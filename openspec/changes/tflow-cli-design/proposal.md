# Proposal: tflow - AI-Powered E2E Test Generation CLI

## Why

Writing and maintaining end-to-end (E2E) tests is a significant pain point for frontend development teams. Tests are time-consuming to write, brittle to maintain, and often don't cover critical user workflows. With AI agents now capable of understanding code structure and generating quality code, we have an opportunity to automate this entire process—**from analyzing a codebase to generating, validating, and managing Playwright tests**.

## What Changes

**New CLI tool `tflow`** - A command-line interface that uses Claude AI to automatically:

- **Analyze** project code structure (routes, components, APIs, tech stack)
- **Infer** core user interaction paths (login flows, CRUD operations, navigation)
- **Generate** Playwright E2E test code with proper selectors and assertions
- **Verify** tests automatically, with self-healing retry logic
- **Manage** test cases in a local SQLite database for cross-project reuse
- **Support** third-party system integration (API calls, database queries, scripts)

**Core commands:**
- `tflow run <project>` - Full pipeline: analyze → generate → verify
- `tflow plan <project>` - Generate test plan for human review before code generation
- `tflow tool add` - Register external system tools (API, DB, script)
- `tflow list` - View managed test cases with filtering
- `tflow verify <project>` - Re-run existing tests with auto-fix

## Capabilities

### New Capabilities

- **project-analysis**: Analyze frontend project structure, detect framework (Vue/React/Angular), extract routes, identify interactive components and API endpoints
- **test-plan-generation**: Generate structured test plans identifying P0/P1/P2 user paths with step-by-step test scenarios
- **playwright-code-generation**: Generate Playwright test code using Page Object patterns, data-testid selectors, and proper async handling
- **test-verification**: Execute Playwright tests, analyze failures, auto-retry with fixes (max 3 attempts)
- **test-case-management**: Persist verified tests to SQLite database with pattern-based tagging (AUTH_FLOW, CRUD_FLOW, DATA_SYNC) for cross-project reuse
- **external-tool-registration**: Register and manage third-party system tools (API endpoints, database queries, shell scripts) with JSON configuration and environment variable substitution
- **tool-bridge-execution**: Runtime bridge executing registered tools from within Playwright tests for cross-system validation scenarios
- **analysis-caching**: Cache project analysis results with file hash-based incremental updates to reduce AI token usage by 90%+
- **dev-server-lifecycle**: Automatically start/stop project dev servers with health-check polling and port detection
- **headed-browser-mode**: Support both headless and headed browser modes for debugging test execution

### Modified Capabilities

- None (new tool)

## Impact

**Technical Stack:**
- Python 3.11+ with Claude Agent SDK
- Playwright for E2E test execution
- SQLite (4 tables: test_cases, test_runs, tools, case_tools)
- Typer CLI framework with Rich terminal output

**Dependencies:**
- External: `claude-agent-sdk`, `playwright`, `typer[all]`, `rich`
- Environment: `ANTHROPIC_API_KEY` required for AI operations

**Project Structure:**
```
tflow/
├── src/tflow/
│   ├── cli.py              # Typer CLI commands
│   ├── core.py             # Main pipeline orchestration
│   ├── agent.py            # Claude Agent invocation
│   ├── analyzer.py         # Project analysis + caching
│   ├── db.py               # SQLite operations
│   ├── server.py           # Dev server management
│   ├── runner.py           # Playwright test runner
│   ├── tool_bridge.py      # External tool execution
│   └── config.py           # Configuration management
└── data/e2e_tests.db       # Local SQLite database
```

**Configuration:**
- Global: `~/.tflow/config.json` (API keys, defaults)
- Project: `<project>/.tflow.json` (server command, output dir, associated tools)

**Estimated Cost:**
- Small project: ~$3.00 per full run
- With caching: ~$0.25 per subsequent run (91% savings)

**User Workflow:**
1. `tflow tool add --ai "register OA system API"` - Register external tools
2. `tflow plan ./my-project` - Review generated test plan
3. `tflow run ./my-project --from-plan e2e-test-plan.md` - Execute with verification
4. `tflow list --project my-project` - View verified test cases
