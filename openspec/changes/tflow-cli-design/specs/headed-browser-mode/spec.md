# Spec: Headed Browser Mode

Capability for running Playwright tests with visible browser window for debugging and observation.

## ADDED Requirements

### Requirement: Support headed browser execution
The system SHALL allow running tests with visible browser window via --headed flag.

#### Scenario: Headed mode flag
- **WHEN** user provides `--headed` flag to `tflow run` or `tflow verify`
- **THEN** system SHALL add `--headed` flag to Playwright command
- **AND** SHALL launch visible browser window
- **AND** SHALL allow user to observe test execution in real-time

#### Scenario: Headless default mode
- **WHEN** --headed flag is not provided
- **THEN** system SHALL run tests in headless mode (Playwright default)
- **AND** SHALL not display any browser window
- **AND** SHALL be suitable for CI/CD environments

### Requirement: Support headed mode in project config
The system SHALL allow projects to default to headed mode.

#### Scenario: Project-level headed setting
- **WHEN** `.tflow.json` config contains `"headed": true`
- **THEN** system SHALL use headed mode by default for that project
- **AND** SHALL allow CLI flag to override project config
- **AND** SHALL respect CLI --headed/--no-headed flags over config

#### Scenario: Global headed default
- **WHEN** `~/.tflow/config.json` contains `"headed": true`
- **THEN** system SHALL use headed mode as global default
- **AND** SHALL allow project config to override global config
- **AND** SHALL allow CLI flags to override both

### Requirement: Respect Playwright headed config
The system SHALL respect existing Playwright configuration files.

#### Scenario: Existing playwright.config.ts
- **WHEN** project has `playwright.config.ts` with `use: { headless: false }`
- **THEN** system SHALL detect existing headed configuration
- **AND** SHALL not add --headed flag (use existing config)
- **AND** SHALL display message about using project's Playwright config

#### Scenario: CLI override of project config
- **WHEN** user provides `--headed` flag despite Playwright config
- **THEN** system SHALL add --headed flag to override project config
- **AND** SHALL display message about CLI override

### Requirement: Display headed mode status
The system SHALL inform user when running in headed mode.

#### Scenario: Startup message
- **WHEN** tests start with --headed flag
- **THEN** system SHALL display "🖥️  headed 模式：浏览器窗口将可见" message
- **AND** SHALL inform user they can observe test execution

#### Scenario: Instructions for headed mode
- **WHEN** running in headed mode
- **THEN** system SHALL display tip about test speed
- **AND** MAY suggest "可以观察测试过程，但执行速度会较慢"

### Requirement: Handle headed mode in CI environments
The system SHALL handle headed mode appropriately in CI/CD.

#### Scenario: CI environment detection
- **WHEN** running in CI environment (CI=true env var)
- **THEN** system SHALL ignore --headed flag if detected
- **AND** SHALL force headless mode in CI
- **AND** SHALL display warning "CI 环境强制使用 headless 模式"

#### Scenario: Virtual display support
- **WHEN** CI environment supports virtual display (Xvfb)
- **THEN** system SHALL allow headed mode with virtual display
- **AND** SHALL not force headless if display is available

### Requirement: Support headed mode in verify command
The system SHALL support --headed flag for `tflow verify` command.

#### Scenario: Verify with headed mode
- **WHEN** user runs `tflow verify <project> --headed`
- **THEN** system SHALL run existing tests with visible browser
- **AND** SHALL add --headed flag to Playwright command
- **AND** SHALL be useful for debugging failing tests

#### Scenario: Verify single file with headed mode
- **WHEN** user runs `tflow verify --file tests/e2e/login.spec.ts --headed`
- **THEN** system SHALL run only specified test file in headed mode
- **AND** SHALL allow focused debugging of specific test

### Requirement: Handle browser selection in headed mode
The system SHALL respect browser choice when running headed.

#### Scenario: Default browser in headed mode
- **WHEN** running tests with --headed and no browser specified
- **THEN** system SHALL use Playwright's default browser (Chromium)
- **AND** SHALL launch Chromium browser window

#### Scenario: Explicit browser selection
- **WHEN** user specifies --project flag for Playwright (e.g., `--project=firefox`)
- **THEN** system SHALL pass project flag to Playwright command
- **AND** SHALL launch specified browser (Firefox/WebKit) in headed mode
- **AND** SHALL require browser to be installed via `npx playwright install`

### Requirement: Display headed mode troubleshooting
The system SHALL provide guidance when headed mode has issues.

#### Scenario: Display not available
- **WHEN** headed mode fails due to no display
- **THEN** system SHALL detect display error
- **AND** SHALL display helpful error message
- **AND** SHALL suggest using headless mode or setting up display

#### Scenario: Browser not installed
- **WHEN** headed browser is not installed
- **THEN** system SHALL detect missing browser error
- **AND** SHALL display message to run `npx playwright install`
- **AND** SHALL list available browsers to install

### Requirement: Support headed mode screenshots
The system SHALL handle screenshots appropriately in headed mode.

#### Scenario: Screenshots in headed mode
- **WHEN** test fails and screenshot is captured
- **THEN** system SHALL still capture screenshot even in headed mode
- **AND** SHALL save screenshot to results directory
- **AND** SHALL not rely on visual observation alone

#### Scenario: Screenshot notification
- **WHEN** screenshot is captured in headed mode
- **THEN** system SHALL display message about screenshot location
- **AND** SHALL allow user to see screenshot even if browser closed

### Requirement: Performance considerations for headed mode
The system SHALL inform users about performance impact of headed mode.

#### Scenario: Performance warning
- **WHEN** running tests in headed mode
- **THEN** system SHALL display that headed mode is slower
- **AND** MAY suggest "对于正常执行，建议使用 headless 模式以获得更好性能"

#### Scenario: Performance metrics
- **WHEN** tests complete in headed mode
- **THEN** system SHALL report execution time
- **AND** MAY compare to typical headless execution time
