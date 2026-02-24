# Spec: Tool Bridge Execution

Capability for executing registered tools from within Playwright tests via runtime bridge.

## ADDED Requirements

### Requirement: Execute tools from Playwright tests
The system SHALL provide a bridge mechanism for calling registered tools during test execution.

#### Scenario: Tool call from test
- **WHEN** Playwright test calls `e2eTools.call('tool_name', params)`
- **THEN** system SHALL execute `tflow tool exec` command via child_process
- **AND** SHALL pass tool_name and params as JSON arguments
- **AND** SHALL return tool result as parsed JSON to test

#### Scenario: Tool execution timeout
- **WHEN** tool execution exceeds 30 seconds
- **THEN** system SHALL terminate tool execution
- **AND** SHALL return error to test with timeout message
- **AND** SHALL include partial output if available

### Requirement: Execute API tools
The system SHALL execute HTTP requests for API-type tools.

#### Scenario: GET request execution
- **WHEN** executing API tool with GET method
- **THEN** system SHALL construct URL with base url and query params
- **AND** SHALL apply headers from config (including auth)
- **AND** SHALL send HTTP GET request
- **AND** SHALL return status code and response data

#### Scenario: POST request execution
- **WHEN** executing API tool with POST method
- **THEN** system SHALL send request body from params
- **AND** SHALL apply Content-Type header
- **AND** SHALL return status code and response data

#### Scenario: Response path extraction
- **WHEN** API tool config specifies response_path
- **THEN** system SHALL extract nested data from response using path
- **AND** SHALL support dot notation (e.g., "data.items")
- **AND** SHALL return extracted data as tool result

#### Scenario: API error handling
- **WHEN** API request returns 4xx or 5xx status
- **THEN** system SHALL raise HTTPError with status code
- **AND** SHALL include response body in error message
- **AND** SHALL propagate error to test for assertion

### Requirement: Execute database query tools
The system SHALL execute SQL queries for database-type tools.

#### Scenario: SQLite query execution
- **WHEN** executing db tool with SQLite connection
- **THEN** system SHALL connect to SQLite database
- **AND** SHALL execute query SQL
- **AND** SHALL return results as array of objects
- **AND** SHALL close connection after query

#### Scenario: MySQL query execution
- **WHEN** executing db tool with MySQL connection
- **THEN** system SHALL connect to MySQL using connection string
- **AND** SHALL substitute credentials from env vars
- **AND** SHALL execute query SQL
- **AND** SHALL return results as array of objects

#### Scenario: PostgreSQL query execution
- **WHEN** executing db tool with PostgreSQL connection
- **THEN** system SHALL connect to PostgreSQL using connection string
- **AND** SHALL execute query SQL
- **AND** SHALL return results as array of objects

#### Scenario: Query parameter override
- **WHEN** tool call includes query parameter
- **THEN** system SHALL use provided query instead of default_query
- **AND** SHALL validate query starts with SELECT or WITH
- **AND** SHALL reject queries with modifying statements

#### Scenario: Database error handling
- **WHEN** database connection or query fails
- **THEN** system SHALL raise DatabaseError with details
- **AND** SHALL include connection string (with credentials masked)
- **AND** SHALL include SQL query and error message

### Requirement: Execute script tools
The system SHALL execute shell scripts for script-type tools.

#### Scenario: Script execution
- **WHEN** executing script tool
- **THEN** system SHALL construct command array: [command, script_path, args...]
- **AND** SHALL substitute parameters into args_template
- **AND** SHALL execute script with subprocess
- **AND** SHALL capture stdout, stderr, and exit code

#### Scenario: Script output capture
- **WHEN** script completes execution
- **THEN** system SHALL return object with exit_code, stdout, stderr fields
- **AND** SHALL include stdout if exit_code is 0
- **AND** SHALL include stderr if exit_code is non-zero

#### Scenario: Script timeout
- **WHEN** script execution exceeds 60 seconds
- **THEN** system SHALL terminate script process
- **AND** SHALL return error with timeout message
- **AND** SHALL include partial output if available

### Requirement: Resolve tool dependencies
The system SHALL ensure required tools are registered before test execution.

#### Scenario: Tool existence check
- **WHEN** test attempts to call tool via e2eTools.call()
- **THEN** system SHALL verify tool exists in database
- **AND** SHALL raise helpful error if tool not found
- **AND** SHALL suggest using `tflow tool add` to register tool

#### Scenario: Project-scoped tools
- **WHEN** project config specifies tools array
- **THEN** system SHALL only allow calls to tools in project's tool list
- **AND** SHALL raise error if test calls unauthorized tool

### Requirement: Generate Playwright helper module
The system SHALL auto-generate e2eTools helper module in test projects.

#### Scenario: Helper module creation
- **WHEN** tests are generated that use tools
- **THEN** system SHALL create `tests/e2e/helpers/e2e-tools.ts`
- **AND** SHALL export e2eTools object with call() method
- **AND** SHALL handle JSON serialization of parameters
- **AND** SHALL handle JSON parsing of result

#### Scenario: Helper module content
- **WHEN** e2e-tools.ts is generated
- **THEN** system SHALL include TypeScript types for parameters and result
- **AND** SHALL use execSync() for synchronous tool execution
- **AND** SHALL set 30 second timeout by default
- **AND** SHALL include helpful comments for usage

### Requirement: Handle tool execution errors
The system SHALL properly propagate errors from tool execution to tests.

#### Scenario: Tool error propagation
- **WHEN** tool execution raises an error
- **THEN** system SHALL serialize error message to JSON
- **AND** SHALL return error via e2eTools.call()
- **AND** SHALL allow test to assert on error properties

#### Scenario: Retry logic for transient failures
- **WHEN** tool fails with transient error (network, timeout)
- **THEN** system MAY retry tool execution up to 2 times
- **AND** SHALL use exponential backoff between retries
- **AND** SHALL return final result or error after retries

### Requirement: Support tool chaining
The system SHALL allow passing output from one tool to another.

#### Scenario: Tool output as input
- **WHEN** test needs to use tool output as parameter to another tool
- **THEN** system SHALL store result from first tool call in variable
- **AND** SHALL allow passing variable as parameter to second tool call
- **AND** SHALL support nested object/array access in parameters

#### Scenario: Parallel tool execution
- **WHEN** test calls multiple tools that don't depend on each other
- **THEN** system SHALL support Promise.all() for parallel execution
- **AND** SHALL wait for all tools to complete before continuing
- **AND** SHALL aggregate results into array

### Requirement: Log tool executions
The system SHALL maintain audit log of tool executions for debugging.

#### Scenario: Execution logging
- **WHEN** tool is executed via bridge
- **THEN** system SHALL log tool name, parameters, timestamp
- **AND** SHALL log execution duration
- **AND** SHALL log success/failure status
- **AND** SHALL write logs to `.tflow/tool-executions.log`

#### Scenario: Debug mode logging
- **WHEN** --verbose flag is set
- **THEN** system SHALL log full tool configuration (with secrets masked)
- **AND** SHALL log full request/response for API tools
- **AND** SHALL log full SQL queries for DB tools
- **AND** SHALL log full stdout/stderr for script tools
