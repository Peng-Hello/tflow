# Spec: Test Verification

Capability for executing Playwright tests and automatically fixing failures through retry logic.

## ADDED Requirements

### Requirement: Execute Playwright tests
The system SHALL run generated Playwright tests and capture results.

#### Scenario: Single test execution
- **WHEN** running a single test file
- **THEN** system SHALL execute `npx playwright test <file>` in project directory
- **AND** SHALL use `--reporter=line` for human-readable output
- **AND** SHALL enable trace with `--trace=on` for debugging

#### Scenario: Multiple test execution
- **WHEN** running multiple tests
- **THEN** system SHALL execute tests sequentially
- **AND** SHALL track individual test pass/fail status
- **AND** SHALL aggregate results for final report

#### Scenario: Test timeout handling
- **WHEN** test execution exceeds timeout
- **THEN** system SHALL terminate test after 120 second default timeout
- **AND** SHALL mark test as failed with timeout error
- **AND** SHALL capture partial output for debugging

### Requirement: Analyze test failures
The system SHALL analyze failed tests to categorize failure type and determine fixability.

#### Scenario: Selector failure analysis
- **WHEN** test fails with "selector not found" error
- **THEN** system SHALL categorize as selector error
- **AND** SHALL attempt to find alternative selector
- **AND** SHALL update test with new selector

#### Scenario: Timeout failure analysis
- **WHEN** test fails with timeout error
- **THEN** system SHALL categorize as wait issue
- **AND** SHALL increase wait timeout or add explicit wait
- **AND** SHALL improve wait strategy (e.g., waitForSelector instead of fixed timeout)

#### Scenario: Assertion failure analysis
- **WHEN** test fails with assertion error
- **THEN** system SHALL categorize as logic error
- **THEN** system SHALL review assertion logic
- **AND** SHALL update assertion to match actual behavior or fix test step

#### Scenario: Environment failure analysis
- **WHEN** test fails due to environment issue (network, server down)
- **THEN** system SHALL categorize as environment issue
- **AND** SHALL mark as ENV_ISSUE without attempting fix
- **AND** SHALL include environment details in error message

### Requirement: Retry failed tests with fixes
The system SHALL attempt to fix and retry failed tests up to a maximum number of attempts.

#### Scenario: Retry loop execution
- **WHEN** test fails
- **THEN** system SHALL attempt fix and retry up to 3 times (configurable via --max-retry)
- **AND** SHALL execute test after each fix attempt
- **AND** SHALL stop retrying after successful run

#### Scenario: Fix attempt tracking
- **WHEN** attempting fixes
- **THEN** system SHALL track attempt number (1, 2, 3)
- **AND** SHALL report "通过 (第 N 次)" on success
- **AND** SHALL mark as "FAILED" after max retries exhausted

#### Scenario: Unfixable failure handling
- **WHEN** Agent determines failure cannot be fixed
- **THEN** system SHALL stop retrying immediately
- **AND** SHALL mark test as FAILED with reason "UNFIXABLE"
- **AND** SHALL save error message to database

### Requirement: Capture test execution artifacts
The system SHALL capture screenshots, traces, and error logs for failed tests.

#### Scenario: Screenshot capture
- **WHEN** test fails
- **THEN** system SHALL capture screenshot at failure point
- **AND** SHALL save to `tests/e2e/results/<test-name>.png`
- **AND** SHALL include screenshot path in database record

#### Scenario: Trace file capture
- **WHEN** test runs with trace enabled
- **THEN** system SHALL generate trace file in `tests/e2e/.trace/`
- **AND** SHALL provide trace file path for debugging
- **AND** SHALL include trace path in error report

#### Scenario: Error message capture
- **WHEN** test fails
- **THEN** system SHALL capture full error output
- **AND** SHALL extract last 500 characters for database storage
- **AND** SHALL preserve full error log in file for reference

### Requirement: Update test status in database
The system SHALL update test case status and run history after verification.

#### Scenario: Successful test recording
- **WHEN** test passes verification
- **THEN** system SHALL update test_cases status to VERIFIED
- **AND** SHALL set verified_at timestamp to current time
- **AND** SHALL insert record into test_runs with passed=true
- **AND** SHALL record duration_ms from test execution

#### Scenario: Failed test recording
- **WHEN** test fails after all retry attempts
- **THEN** system SHALL update test_cases status to FAILED
- **AND** SHALL store error_msg from last failure
- **AND** SHALL increment retry_count
- **AND** SHALL insert record into test_runs with passed=false and error details

### Requirement: Support headed browser mode
The system SHALL support running tests with visible browser window for debugging.

#### Scenario: Headed mode execution
- **WHEN** --headed flag is provided
- **THEN** system SHALL add --headed flag to Playwright command
- **AND** SHALL launch visible browser window
- **AND** SHALL allow user to observe test execution

#### Scenario: Headless default mode
- **WHEN** --headed flag is not provided
- **THEN** system SHALL run tests in headless mode (default)
- **AND** SHALL not display browser window

### Requirement: Dry run mode
The system SHALL support generating tests without running verification.

#### Scenario: Dry run execution
- **WHEN** --dry-run flag is provided
- **THEN** system SHALL generate test files only
- **AND** SHALL skip verification step
- **AND** SHALL output "dry-run 模式，跳过验证" message

### Requirement: Report verification progress
The system SHALL provide real-time feedback on verification progress.

#### Scenario: Progress reporting
- **WHEN** verifying tests
- **THEN** system SHALL output test file name with emoji status
- **AND** SHALL show "🧪 验证: tests/e2e/login.spec.ts" at start
- **AND** SHALL show "✅ 通过 (第 N 次)" on success
- **AND** SHALL show "❌ → 🔧 修复 → ✅" on retry success
- **AND** SHALL show "⚠️ 失败" on final failure

#### Scenario: Summary report
- **WHEN** all tests verified
- **THEN** system SHALL output summary table with total, passed, failed counts
- **AND** SHALL calculate and display pass percentage
- **AND** SHALL display total LLM cost for the run
