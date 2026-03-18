# Design: tflow - AI-Powered E2E Test Generation CLI

## Context

**Background:**
Frontend teams spend significant time writing and maintaining E2E tests. The V1-V4 design documents outline an evolution from a complex multi-agent architecture to a pragmatic single-agent solution with Python orchestration. The documentation shows a clear progression: V1 (over-engineered 5+ agents) → V2 (simplified 1 agent) → V3 (CLI tooling) → V4 (cross-system integration).

**Current State:**
- No automated E2E test generation exists
- Teams write tests manually or skip E2E coverage entirely
- Test maintenance is a significant burden
- Cross-system integration tests require custom infrastructure

**Constraints:**
- Must use Claude Agent SDK (Anthropic)
- Cost sensitivity: AI token usage must be minimized
- Local-first: No server deployment, runs as CLI tool
- Language: Python 3.11+ required by Claude Agent SDK

**Stakeholders:**
- Frontend developers (primary users)
- QA teams (secondary users for test review)
- DevOps (CI/CD integration)

## Goals / Non-Goals

**Goals:**
1. **Automated test generation** - Analyze code and generate Playwright tests without manual intervention
2. **Self-healing tests** - Auto-retry with fix attempts (max 3) before marking as failed
3. **Cross-project reuse** - Store verified tests in SQLite with pattern matching for future projects
4. **Third-party integration** - Support API calls, database queries, and script execution for cross-system validation
5. **Developer-friendly** - Simple CLI interface with helpful output and configuration management
6. **Cost-efficient** - Analysis caching to reduce AI usage by 90%+ on subsequent runs

**Non-Goals:**
- Visual regression testing
- Performance/load testing
- Mobile app testing (web browsers only)
- Multi-user cloud deployment (local-only tool)
- Support for testing frameworks other than Playwright

## Decisions

### D1: Single Agent with Python Orchestration

**Decision:** Use 1 Claude Agent for "understanding" tasks (code analysis, test generation, failure debugging) while using Python code for deterministic orchestration (flow control, database operations, process management).

**Rationale:**
- LLMs are expensive and non-deterministic—only use them where "understanding" is required
- Python code is free, fast, and 100% reliable for control flow
- V1's 5-agent approach was over-engineered; V2's simplified approach reduces cost by 50%+
- Clear separation: Agent = intelligence, Python = execution

**Alternatives Considered:**
- *Multi-agent (V1)*: Rejected due to high cost and complexity
- *Pure LLM orchestration*: Rejected due to non-determinism and cost
- *Rule-based test generation*: Rejected due to inability to understand complex UI patterns

### D2: SQLite with 4 Tables

**Decision:** Use SQLite with 4 tables: `test_cases`, `test_runs`, `tools`, `case_tools`.

**Rationale:**
- SQLite is embedded (no separate database server required)
- 4 tables balance simplicity with functionality
- V2's 2-table design was insufficient for tool integration
- V1's 6-table design with UUIDs and complex relationships was overkill

**Schema:**
```sql
test_cases:      id, project, name, pattern, file_path, code, status, created_at
test_runs:       id, case_id, passed, error_msg, duration_ms, run_at
tools:           id, name, system, type (api/db_query/script), config, params_schema
case_tools:      id, case_id, tool_id, phase (before/after/verify), purpose, params
```

**Alternatives Considered:**
- *JSON file storage*: Rejected due to poor query performance for filtering/joining
- *PostgreSQL/MySQL*: Rejected due to deployment complexity
- *V1's 6-table schema*: Rejected due to complexity (tags, reuse_links unnecessary for MVP)

### D3: File Hash-Based Analysis Caching

**Decision:** Cache project analysis results with MD5 hash tracking for incremental updates.

**Rationale:**
- Full project analysis costs ~$0.54 (80K tokens) for medium projects
- 90% of files don't change between runs—reevaluating is wasteful
- MD5 hash comparison detects changes instantly
- Saves 91% on AI costs after first run ($0.54 → $0.05)

**Cache Structure:**
```json
{
  "version": "1.0",
  "analyzed_at": "2026-02-24T22:50:00",
  "file_hashes": { "src/router/index.ts": "a1b2c3d4", ... },
  "routes": [...], "api_calls": [...], "components": [...]
}
```

**Alternatives Considered:**
- *No caching*: Rejected due to cost
- *Time-based expiration*: Rejected due to stale data risk
- *Git-based diff*: Rejected due to dependency on git state

### D4: Tool Registration with JSON Schema

**Decision:** External tools registered via JSON configuration with `params_schema` for AI parameter discovery.

**Rationale:**
- AI needs to know what parameters a tool accepts to generate correct calls
- JSON schema provides type safety (string, integer, enum, required/optional)
- Environment variable substitution (`{{env.TOKEN}}`) keeps secrets out of config
- Supports three tool types covering most cross-system scenarios

**Tool Types:**
- `api`: HTTP endpoints with headers/auth
- `db_query`: Database SELECT queries
- `script`: Shell script execution

**Alternatives Considered:**
- *Hardcoded tools*: Rejected due to lack of flexibility
- *Python plugin system*: Rejected due to complexity and security risk
- *No params_schema*: Rejected because AI would guess parameters incorrectly

### D5: Two-Stage Workflow (Plan → Execute)

**Decision:** Support two modes: (1) `tflow plan` generates reviewable test plan, (2) `tflow run --from-plan` executes after human approval.

**Rationale:**
- AI may misinterpret user intent—human review catches issues early
- Some tests require domain knowledge (e.g., business rules)
- Plan file is editable Markdown—users can add/remove/modify tests
- Direct `tflow run` still available for fully automated scenarios

**Alternatives Considered:**
- *Generate code directly*: Rejected due to lack of control
- *Interactive approval prompts*: Rejected due to poor UX for bulk changes
- *Web UI*: Rejected due to complexity (CLI tool scope)

### D6: Configuration Hierarchy

**Decision:** Three-tier config priority: CLI args > project config > global config > defaults.

**Rationale:**
- Global config (`~/.tflow/config.json`) for user preferences (API key, defaults)
- Project config (`.tflow.json`) for project-specific settings (server command, tools)
- CLI args for one-off overrides
- Mirrors common tool patterns (git, docker)

**Alternatives Considered:**
- *Single config file*: Rejected due to lack of project-specific customization
- *Environment variables only*: Rejected due to poor UX for complex config
- *YAML config*: Rejected in favor of JSON (simpler, no external dep)

## Risks / Trade-offs

### R1: AI Hallucination → High-Quality Prompt Engineering

**Risk:** Agent may generate syntactically correct but semantically wrong tests (e.g., wrong selectors, missing assertions).

**Mitigation:**
- Provide `tflow plan` for human review before code generation
- Include verified test examples in prompt (few-shot learning)
- Use structured output format (JSON) for test summaries
- Auto-verify all generated tests before marking as VERIFIED

### R2: Cost Accumulation → Caching + Budget Limits

**Risk:** Frequent runs on large projects could accumulate high AI costs.

**Mitigation:**
- File hash caching reduces cost by 91% on subsequent runs
- `--max-budget` flag sets hard dollar limit per run
- `--dry-run` mode generates code without verification (no retry costs)
- Detailed cost reporting after each run

### R3: Tool Security → Sandboxed Execution

**Risk:** Registered tools (especially script type) could execute malicious commands.

**Mitigation:**
- Tools require explicit registration via `tflow tool add` (no auto-discovery)
- Script tools only execute pre-registered paths (no dynamic commands)
- DB tools only allow SELECT queries (no INSERT/UPDATE/DELETE)
- API tool configs support rate limiting
- Environment variables keep secrets out of stored configs

### R4: Project Detection Accuracy → Multi-Framework Support

**Risk:** Code analysis may fail on uncommon frameworks or custom routing.

**Mitigation:**
- Start with Vue 3, React, Angular, Next.js (90%+ coverage)
- Fallback to generic analysis when framework not detected
- Users can manually specify tech stack via project config
- Analysis cache is editable for manual corrections

### R5: Dev Server Port Conflicts → Auto Port Detection

**Risk:** Default dev server port may already be in use.

**Mitigation:**
- `DevServer` class uses `socket.bind(("", 0)")` to find free port
- Configurable via `server-port` in `.tflow.json`
- `--server-url` flag allows connecting to already-running server
- Health check polling with 30s timeout (not blind `sleep(10)`)

## Migration Plan

**Phase 1: Development (Week 1-2)**
- Set up project structure and dependencies
- Implement core modules (db, agent, runner, server)
- Implement basic `tflow run` for single-system projects
- Test on 2-3 sample projects

**Phase 2: CLI Enhancement (Week 3)**
- Add all CLI commands (plan, verify, list, config)
- Implement Rich terminal output formatting
- Add configuration management
- User testing with internal team

**Phase 3: Cross-System Integration (Week 4)**
- Implement tool registration and bridge execution
- Add `tflow tool` subcommands
- Test with real cross-system scenarios (OA API + local DB)
- Security review of tool execution

**Phase 4: Polish & Documentation (Week 5)**
- Add analysis caching
- Write comprehensive README and examples
- Package for pip install
- Beta testing with external users

**Rollback Strategy:**
- Tool is locally installed via `pip install tflow`—no server infrastructure
- Uninstall via `pip uninstall tflow` removes everything
- SQLite database at `~/.tflow/data/e2e_tests.db` can be deleted manually
- No system-wide dependencies or configuration changes

## Open Questions

1. **Q: Should we support non-Python testing frameworks (Cypress, TestCafe)?**
   - **A:** No. Playwright only for V1. Revisit if strong user demand exists.

2. **Q: Should test plans support version control (diff between runs)?**
   - **A:** Out of scope for MVP. Git can track plan file changes if needed.

3. **Q: How to handle authentication in generated tests?**
   - **A:** Agent will detect auth patterns (localStorage, cookies, tokens) and generate appropriate setup. Users can edit plan to add custom auth steps.

4. **Q: Should we support parallel test execution?**
   - **A:** Playwright supports this natively via `workers` config. We'll pass through but not optimize in V1.

5. **Q: What's the long-term maintenance plan for tool definitions?**
   - **A:** Consider a "tool marketplace" (team-shared JSON repo) in V4.1. For now, users register tools per-project.
