# Spec: External Tool Registration

Capability for registering and managing third-party system tools (API, database, script) for cross-system validation.

## ADDED Requirements

### Requirement: Register API tools
The system SHALL support registering HTTP API endpoints as callable tools.

#### Scenario: API tool registration
- **WHEN** user runs `tflow tool add --type api`
- **THEN** system SHALL require name, system, description, and config
- **AND** SHALL store config JSON with method, url, headers, params
- **AND** SHALL support environment variable substitution via {{env.VAR}} syntax
- **AND** SHALL validate config structure before saving

#### Scenario: API tool with authentication
- **WHEN** registering API tool with auth
- **THEN** system SHALL support headers with Authorization field
- **AND** SHALL accept {{env.TOKEN_NAME}} for bearer tokens
- **AND** SHALL not store actual token values in config

### Requirement: Register database query tools
The system SHALL support registering database queries as callable tools.

#### Scenario: Database tool registration
- **WHEN** user runs `tflow tool add --type db_query`
- **THEN** system SHALL require connection_string and default_query
- **AND** SHALL support {{env.VAR}} for credentials in connection string
- **AND** SHALL only allow SELECT queries (reject INSERT/UPDATE/DELETE)
- **AND** SHALL support multiple database types (SQLite, MySQL, PostgreSQL)

#### Scenario: Query parameter override
- **WHEN** database tool is called with custom query
- **THEN** system SHALL accept query parameter to override default_query
- **AND** SHALL validate query starts with SELECT or WITH
- **AND** SHALL reject queries with modifying statements

### Requirement: Register script tools
The system SHALL support registering shell scripts as callable tools.

#### Scenario: Script tool registration
- **WHEN** user runs `tflow tool add --type script`
- **THEN** system SHALL require command, script_path, and args_template
- **AND** SHALL validate script_path exists
- **AND** SHALL store args_template as string with parameter placeholders
- **AND** SHALL execute script with subprocess when called

#### Scenario: Script tool safety
- **WHEN** registering script tool
- **THEN** system SHALL only allow pre-registered script paths
- **AND** SHALL reject scripts with user-provided paths at call time
- **AND** SHALL capture stdout, stderr, and exit code in result

### Requirement: Support AI-assisted tool registration
The system SHALL generate tool configuration from natural language descriptions.

#### Scenario: AI tool generation
- **WHEN** user runs `tflow tool add --ai "description"`
- **THEN** system SHALL invoke Claude Agent to generate config
- **AND** SHALL infer tool type from description (API/DB/script)
- **AND** SHALL generate appropriate config structure
- **AND** SHALL generate params_schema with type, required, description

#### Scenario: AI tool confirmation
- **WHEN** AI generates tool configuration
- **THEN** system SHALL display generated config in formatted table
- **AND** SHALL prompt for confirmation [Y/n/edit]
- **AND** SHALL save tool on Y confirmation
- **AND** SHALL allow user to edit before saving on 'edit' response

### Requirement: Define tool parameter schema
The system SHALL support parameter schema declaration for AI understanding.

#### Scenario: Params schema structure
- **WHEN** defining params_schema
- **THEN** system SHALL accept JSON object with parameter names as keys
- **AND** SHALL support type field (string, integer, boolean, array)
- **AND** SHALL support required field (true/false)
- **AND** SHALL support description field for parameter purpose
- **AND** SHALL support enum field for allowed values
- **AND** SHALL support default field for default value

#### Scenario: Schema validation
- **WHEN** tool is called with parameters
- **THEN** system SHALL validate parameters against params_schema
- **AND** SHALL reject call if required parameters missing
- **AND** SHALL use default values for optional parameters not provided
- **AND** SHALL validate enum values when enum field present

### Requirement: List registered tools
The system SHALL display all registered tools in table format.

#### Scenario: Tool list display
- **WHEN** user runs `tflow tool list`
- **THEN** system SHALL display table with ID, name, system, type, description columns
- **AND** SHALL support filtering by --system flag
- **AND** SHALL support JSON output via --json flag

#### Scenario: Tool detail view
- **WHEN** user runs `tflow tool list <name>`
- **THEN** system SHALL display full tool configuration
- **AND** SHALL show config and params_schema in formatted output

### Requirement: Test tool connectivity
The system SHALL verify tool connectivity and functionality.

#### Scenario: API tool test
- **WHEN** user runs `tflow tool test <api-tool-name>`
- **THEN** system SHALL execute HTTP request with tool config
- **AND** SHALL display response status, data length, and duration
- **AND** SHALL show ✅ success or ❌ failure with error message

#### Scenario: Database tool test
- **WHEN** user runs `tflow tool test <db-tool-name>`
- **THEN** system SHALL execute default_query
- **AND** SHALL display row count and first few results
- **AND** SHALL show connection error if database unreachable

#### Scenario: Test all tools
- **WHEN** user runs `tflow tool test --all`
- **THEN** system SHALL test all registered tools sequentially
- **AND** SHALL display results for each tool
- **AND** SHALL show summary of passed/failed tool tests

### Requirement: Remove registered tools
The system SHALL support deletion of registered tools.

#### Scenario: Single tool removal
- **WHEN** user runs `tflow tool remove <name>`
- **THEN** system SHALL prompt for confirmation
- **AND** SHALL delete tool from tools table on confirmation
- **AND** SHALL cascade delete related case_tools records

#### Scenario: Batch tool import
- **WHEN** user runs `tflow tool import <tools.json>`
- **THEN** system SHALL read JSON array of tool definitions
- **AND** SHALL validate each tool definition
- **AND** SHALL insert valid tools into database
- **AND** SHALL report import summary (added, skipped, failed)

### Requirement: Associate tools with test cases
The system SHALL link tools to test cases for cross-system validation.

#### Scenario: Tool association
- **WHEN** test case requires external tool
- **THEN** system SHALL create record in case_tools table
- **AND** SHALL link case_id and tool_id
- **AND** SHALL specify phase (before/after/verify)
- **AND** SHALL store purpose description

#### Scenario: Multiple tools per test
- **WHEN** test case requires multiple tools
- **THEN** system SHALL support multiple case_tools records
- **AND** SHALL allow tools in same or different phases
- **AND** SHALL preserve tool call order via sequence field

### Requirement: Resolve environment variables in config
The system SHALL substitute environment variable placeholders at runtime.

#### Scenario: Env var substitution
- **WHEN** tool config contains {{env.VAR_NAME}}
- **THEN** system SHALL read VAR_NAME from environment at execution time
- **AND** SHALL replace {{env.VAR_NAME}} with actual value
- **AND** SHALL raise error if required env var not set

#### Scenario: Nested env var resolution
- **WHEN** config has nested objects with {{env.VAR}}
- **THEN** system SHALL recursively resolve all env var placeholders
- **AND** SHALL handle env vars in headers, URLs, connection strings

### Requirement: Store tool configuration securely
The system SHALL never store secrets in tool configurations.

#### Scenario: Secret handling
- **WHEN** registering tool with secrets (passwords, tokens)
- **THEN** system SHALL require {{env.VAR}} syntax for secret values
- **AND** SHALL reject plaintext secrets in config
- **AND** SHALL store only placeholder references in database

#### Scenario: Config validation
- **WHEN** saving tool config
- **THEN** system SHALL scan for plaintext secret patterns
- **AND** SHALL warn if potential secret detected
- **AND** SHALL suggest using environment variable instead
