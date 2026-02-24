# Implementation Tasks: tflow CLI Tool

## 1. Project Setup & Infrastructure

- [x] 1.1 Create Python package structure with `src/tflow/` directory
- [x] 1.2 Create `pyproject.toml` with dependencies (claude-agent-sdk, typer, rich, playwright)
- [x] 1.3 Create CLI entry point in `src/tflow/cli.py` with Typer app
- [x] 1.4 Set up SQLite database initialization in `src/tflow/db.py`
- [x] 1.5 Create configuration management in `src/tflow/config.py`
- [x] 1.6 Add Rich console output utilities in `src/tflow/reporter.py`

## 2. Database Layer

- [x] 2.1 Implement `init_db()` function to create 4 tables (test_cases, test_runs, tools, case_tools)
- [x] 2.2 Implement `save_case()` to insert/update test case records
- [x] 2.3 Implement `query_cases()` with filters (project, pattern, status)
- [x] 2.4 Implement tool registration functions (add_tool, get_tool, list_tools)
- [x] 2.5 Implement `save_test_run()` to record test execution history
- [x] 2.6 Implement reusability score calculation logic

## 3. Project Analysis

- [x] 3.1 Implement file hash calculation for caching (MD5)
- [x] 3.2 Implement project scanner for source files (.vue, .tsx, .ts, .jsx, .js, .svelte)
- [x] 3.3 Implement cache loader/saver functions
- [x] 3.4 Implement incremental analysis logic (changed file detection)
- [x] 3.5 Implement Claude Agent invocation for code analysis
- [x] 3.6 Add tech stack detection (Vue 3, React, Angular, Next.js)
- [x] 3.7 Add route extraction from router config files
- [x] 3.8 Add API endpoint detection from source code
- [x] 3.9 Add component identification (forms, tables, modals)
- [x] 3.10 Add authentication flow detection

## 4. Test Plan Generation

- [x] 4.1 Implement path inference logic (P0/P1/P2 prioritization)
- [x] 4.2 Implement pattern matching (AUTH_FLOW, CRUD_FLOW, DATA_SYNC, etc.)
- [x] 4.3 Implement test plan Markdown generation
- [x] 4.4 Add tool integration identification in test plans
- [x] 4.5 Implement editable test plan format with user comments
- [x] 4.6 Add `tflow plan` CLI command

## 5. Playwright Code Generation

- [x] 5.1 Implement Agent prompt for test code generation
- [x] 5.2 Add Page Object Model pattern generation
- [x] 5.3 Implement selector strategy (data-testid priority)
- [x] 5.4 Add async/await handling generation
- [x] 5.5 Implement assertion generation (URL, visibility, data)
- [x] 5.6 Add beforeEach/afterEach setup generation
- [x] 5.7 Implement external tool call syntax generation
- [x] 5.8 Add authentication handling in test generation
- [x] 5.9 Generate e2eTools helper module (`tests/e2e/helpers/e2e-tools.ts`)

## 6. Dev Server Management

- [x] 6.1 Implement `DevServer` class in `src/tflow/server.py`
- [x] 6.2 Add free port detection using socket.bind(("", 0"))
- [x] 6.3 Implement server start with process spawning
- [x] 6.4 Add health check polling for server readiness
- [x] 6.5 Implement graceful shutdown with timeout
- [x] 6.6 Add server output capture and buffering
- [x] 6.7 Handle Vite/Next.js config detection
- [x] 6.8 Support custom server commands via config

## 7. Test Execution & Verification

- [x] 7.1 Implement Playwright test runner in `src/tflow/runner.py`
- [x] 7.2 Add test execution with subprocess management
- [x] 7.3 Implement output parsing for pass/fail detection
- [x] 7.4 Add screenshot and trace capture on failure
- [x] 7.5 Implement failure analysis (selector, timeout, assertion, environment)
- [x] 7.6 Add retry loop with max 3 attempts
- [x] 7.7 Implement Agent-based test fixing
- [x] 7.8 Add headed mode support (`--headed` flag)
- [x] 7.9 Implement dry-run mode (generate without executing)

## 8. External Tool System

- [x] 8.1 Implement tool registration in database
- [x] 8.2 Add API tool type execution (HTTP requests)
- [x] 8.3 Add DB query tool type execution (SQLite, MySQL, PostgreSQL)
- [x] 8.4 Add script tool type execution (subprocess)
- [x] 8.5 Implement environment variable substitution (`{{env.VAR}}`)
- [x] 8.6 Add params_schema validation
- [x] 8.7 Implement AI-assisted tool registration (`tflow tool add --ai`)
- [x] 8.8 Add tool testing functionality (`tflow tool test`)

## 9. Tool Bridge Execution

- [x] 9.1 Implement `tool_bridge.py` for tool execution
- [x] 9.2 Add `tflow tool exec` command for bridge calls
- [x] 9.3 Implement JSON serialization for parameters/results
- [x] 9.4 Add error handling and propagation to tests
- [x] 9.5 Implement tool execution logging
- [x] 9.6 Add timeout handling for tool calls

## 10. CLI Commands

- [x] 10.1 Implement `tflow run` command (full pipeline)
- [x] 10.2 Implement `tflow plan` command (test plan generation)
- [x] 10.3 Implement `tflow analyze` command (analysis only)
- [x] 10.4 Implement `tflow verify` command (run existing tests)
- [x] 10.5 Implement `tflow list` command (list test cases)
- [x] 10.6 Implement `tflow export` command (export test files)
- [x] 10.7 Implement `tflow config` command (config management)
- [x] 10.8 Implement `tflow tool add/list/test/remove/import` commands
- [x] 10.9 Implement `tflow cache status/clear` commands
- [x] 10.10 Add Rich table formatting for list commands

## 11. Configuration Management

- [x] 11.1 Implement global config loader (`~/.tflow/config.json`)
- [x] 11.2 Implement project config loader (`.tflow.json`)
- [x] 11.3 Add config priority logic (CLI > project > global > defaults)
- [x] 11.4 Add `tflow config show` command
- [x] 11.5 Add `tflow config set` command
- [x] 11.6 Implement secret handling (env var substitution)

## 12. Main Pipeline Orchestration

- [x] 12.1 Implement `run_pipeline()` function in `src/tflow/core.py`
- [x] 12.2 Orchestrate: server start → analysis → plan generation → test generation → verification → report
- [x] 12.3 Implement from-plan mode (read and execute test plan)
- [x] 12.4 Add progress reporting with Rich output
- [x] 12.5 Implement cost tracking and reporting
- [x] 12.6 Add final report generation (coverage, pass rate, cost)

## 13. Agent Integration

- [x] 13.1 Implement Agent invocation wrapper in `src/tflow/agent.py`
- [x] 13.2 Add context building for analysis prompt
- [x] 13.3 Add context building for test generation prompt
- [x] 13.4 Add context building for test fixing prompt
- [x] 13.5 Implement tool context formatting for Agent
- [x] 13.6 Add existing cases context for reuse

## 14. Testing & Quality

- [x] 14.1 Write unit tests for db.py functions
- [x] 14.2 Write unit tests for analyzer.py (hash, cache logic)
- [x] 14.3 Write unit tests for tool_bridge.py (all tool types)
- [x] 14.4 Write integration test for full pipeline with sample project
- [x] 14.5 Add error handling tests (server crash, tool failure, etc.)
- [x] 14.6 Add config validation tests

## 15. Documentation & Polish

- [x] 15.1 Write README.md with installation and quick start
- [x] 15.2 Add example for each CLI command
- [x] 15.3 Write cross-system integration tutorial
- [x] 15.4 Add troubleshooting guide
- [x] 15.5 Add cost optimization tips
- [x] 15.6 Prepare package for pip install
- [x] 15.7 Add version numbering and changelog
