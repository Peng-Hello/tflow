# Spec: Playwright Code Generation

Capability for generating Playwright test code using best practices with proper selectors, assertions, and async handling.

## ADDED Requirements

### Requirement: Generate Playwright test files
The system SHALL generate `.spec.ts` test files following Playwright Test Runner conventions.

#### Scenario: Test file structure
- **WHEN** generating test file for a test case
- **THEN** system SHALL create file at `tests/e2e/<name>.spec.ts`
- **AND** SHALL include import statement for `test, expect` from '@playwright/test'
- **AND** SHALL wrap tests in `test.describe()` block with descriptive name
- **AND** SHALL use `test()` blocks for individual test scenarios

#### Scenario: Pattern annotation in test files
- **WHEN** generating test file
- **THEN** system SHALL include comment header with pattern type
- **AND** SHALL format: `// pattern: AUTH_FLOW` or `// pattern: CRUD_FLOW`
- **AND** SHALL include tools comment if external tools used: `// tools: oa_api, local_db`

### Requirement: Use Page Object Model patterns
The system SHALL generate tests using Page Object Model best practices for maintainability.

#### Scenario: Selector strategy
- **WHEN** generating test code
- **THEN** system SHALL prioritize `data-testid` selectors
- **AND** SHALL fallback to role-based selectors (`getByRole`)
- **AND** SHALL avoid fragile CSS selectors as last resort
- **AND** SHALL use `getByTestId()`, `getByRole()`, `getByText()`, `getByLabel()` methods

#### Scenario: Page interaction patterns
- **WHEN** generating page interactions
- **THEN** system SHALL use explicit waits with `waitForSelector()` for dynamic elements
- **AND** SHALL use `waitForURL()` for navigation assertions
- **AND** SHALL use `waitForLoadState()` for network idle when needed
- **AND** SHALL avoid hard-coded `sleep()` calls

### Requirement: Generate proper test assertions
The system SHALL generate meaningful assertions to verify expected outcomes.

#### Scenario: URL assertions
- **WHEN** testing navigation
- **THEN** system SHALL assert URL with `expect(page).toHaveURL()`
- **AND** SHALL support regex patterns for dynamic URLs
- **AND** SHALL include base URL handling

#### Scenario: Element visibility assertions
- **WHEN** testing UI elements
- **THEN** system SHALL assert visibility with `expect(element).toBeVisible()`
- **AND** SHALL assert text content with `expect(element).toContainText()`
- **AND** SHALL assert element count with `expect(elements).toHaveCount()`

#### Scenario: Data assertions
- **WHEN** testing data display
- **THEN** system SHALL assert data values match expected
- **AND** SHALL support array/object comparisons
- **AND** SHALL include tolerance for numeric values when appropriate

### Requirement: Handle asynchronous operations
The system SHALL generate code with proper async/await handling for all asynchronous operations.

#### Scenario: Async test functions
- **WHEN** generating test functions
- **THEN** system SHALL use `async ({ page }) => {}` arrow function syntax
- **AND** SHALL await all page interactions
- **AND** SHALL await all assertions

#### Scenario: API request handling
- **WHEN** testing API-driven interactions
- **THEN** system SHALL wait for API responses using `waitForResponse()`
- **AND** SHALL assert response status and data
- **AND** SHALL handle loading states appropriately

### Requirement: Generate setup and teardown
The system SHALL generate appropriate test setup and teardown code.

#### Scenario: beforeEach navigation
- **WHEN** generating test with multiple scenarios
- **THEN** system SHALL include `test.beforeEach()` block
- **AND** SHALL navigate to starting page in beforeEach
- **AND** SHALL reset test state if needed

#### Scenario: Test isolation
- **WHEN** generating tests that modify data
- **THEN** system SHALL ensure test data isolation
- **AND** SHALL clean up created data in `test.afterEach()` if appropriate
- **AND** SHALL use unique identifiers for test data

### Requirement: Include external tool calls
The system SHALL generate code to call external tools when required by test scenario.

#### Scenario: Tool call syntax
- **WHEN** test requires external tool
- **THEN** system SHALL import e2eTools helper: `import { e2eTools } from './helpers/e2e-tools'`
- **AND** SHALL call tool with `await e2eTools.call('tool_name', params)`
- **AND** SHALL assign result to variable for assertions

#### Scenario: Before-phase tool calls
- **WHEN** tool is used in before phase
- **THEN** system SHALL call tool at test start, before page interactions
- **AND** SHALL store result for later comparison
- **AND** SHALL handle tool errors gracefully

#### Scenario: After-phase tool calls
- **WHEN** tool is used in after phase
- **THEN** system SHALL call tool after page interactions complete
- **AND** SHALL use tool result for final assertions
- **AND** SHALL compare before/after results if applicable

### Requirement: Generate descriptive test names
The system SHALL generate clear, descriptive test names following best practices.

#### Scenario: Test naming convention
- **WHEN** generating test names
- **THEN** system SHALL use "should <expected outcome>" format
- **AND** SHALL be specific about what is being tested
- **AND** SHALL avoid vague names like "test1" or "works"

#### Scenario: Describe block naming
- **WHEN** generating describe blocks
- **THEN** system SHALL use feature or user story name
- **AND** SHALL group related tests logically
- **AND** SHALL follow user-centric language

### Requirement: Add comments for complex logic
The system SHALL add explanatory comments for complex test logic.

#### Scenario: Selector comments
- **WHEN** using complex selectors
- **THEN** system SHALL add comment explaining selector choice
- **AND** SHALL note if selector is fallback from preferred option

#### Scenario: Assertion comments
- **WHEN** making non-obvious assertions
- **THEN** system SHALL add comment explaining assertion rationale
- **AND** SHALL document business rules being verified

### Requirement: Handle authentication in tests
The system SHALL generate code to handle authentication flows.

#### Scenario: Login before auth tests
- **WHEN** generating authenticated test
- **THEN** system SHALL include login step in beforeEach
- **AND** SHALL navigate to login page
- **AND** SHALL enter credentials and submit
- **AND** SHALL verify authentication success

#### Scenario: Token storage handling
- **WHEN** app uses token-based auth
- **THEN** system SHALL verify token storage (localStorage/cookie)
- **AND** SHALL include token in subsequent requests if needed
- **AND** SHALL handle token expiration scenarios
