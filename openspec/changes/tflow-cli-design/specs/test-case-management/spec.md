# Spec: Test Case Management

Capability for persisting and managing test cases in SQLite database with cross-project reuse.

## ADDED Requirements

### Requirement: Store test cases in database
The system SHALL persist generated and verified test cases to SQLite database.

#### Scenario: New test case creation
- **WHEN** test case is generated and verified
- **THEN** system SHALL insert record into test_cases table
- **AND** SHALL store project name, test name, pattern type
- **AND** SHALL store file path and complete code content
- **AND** SHALL set initial status to DRAFT
- **AND** SHALL update status to VERIFIED after successful verification

#### Scenario: Test case update
- **WHEN** existing test case is re-verified
- **THEN** system SHALL update code_content field with new code
- **AND** SHALL update status based on verification result
- **AND** SHALL update verified_at timestamp if VERIFIED

### Requirement: Track test run history
The system SHALL maintain historical record of all test executions.

#### Scenario: Test run recording
- **WHEN** test is executed
- **THEN** system SHALL insert record into test_runs table
- **AND** SHALL link to test_case via case_id foreign key
- **AND** SHALL record passed (boolean), error_msg, duration_ms
- **AND** SHALL timestamp run_at with current time

#### Scenario: Run history query
- **WHEN** querying test history
- **THEN** system SHALL return all runs for a test case ordered by time
- **AND** SHALL show pass/fail trend over time
- **AND** SHALL include error messages for failed runs

### Requirement: Query test cases with filters
The system SHALL support querying test cases with various filters.

#### Scenario: Query by project
- **WHEN** filtering by project name
- **THEN** system SHALL return all test cases for specified project
- **AND** SHALL support partial name matching

#### Scenario: Query by pattern
- **WHEN** filtering by pattern type
- **THEN** system SHALL return all test cases matching pattern (AUTH_FLOW, CRUD_FLOW, etc.)
- **AND** SHALL support exact pattern matching

#### Scenario: Query by status
- **WHEN** filtering by status
- **THEN** system SHALL return all test cases with specified status (DRAFT, VERIFIED, FAILED)
- **AND** SHALL support multiple status filter

#### Scenario: Combined filters
- **WHEN** using multiple filters (project + pattern + status)
- **THEN** system SHALL apply all filters with AND logic
- **AND** SHALL return only matching test cases

### Requirement: Calculate test coverage statistics
The system SHALL generate coverage reports from test case data.

#### Scenario: Coverage by priority
- **WHEN** generating coverage report
- **THEN** system SHALL group test cases by priority
- **AND** SHALL count total and verified per priority
- **AND** SHALL calculate coverage percentage
- **AND** SHALL output table with priority, total, verified, coverage_pct columns

#### Scenario: Coverage by project
- **WHEN** generating project coverage
- **THEN** system SHALL filter by project name
- **AND** SHALL count total, verified, failed test cases
- **AND** SHALL calculate overall pass percentage

### Requirement: Export test cases
The system SHALL support exporting verified test cases to file system.

#### Scenario: Export by project
- **WHEN** exporting test cases for a project
- **THEN** system SHALL query all VERIFIED test cases for project
- **AND** SHALL write each test case to separate file in output directory
- **AND** SHALL use original file name from file_path field

#### Scenario: Export by pattern
- **WHEN** exporting test cases by pattern
- **THEN** system SHALL query all VERIFIED test cases matching pattern
- **AND** SHALL write to output directory preserving original structure

### Requirement: List test cases in table format
The system SHALL display test cases in formatted table for CLI output.

#### Scenario: Table display
- **WHEN** running `tflow list` command
- **THEN** system SHALL display table with ID, project, name, pattern, status columns
- **AND** SHALL format table with borders and aligned columns
- **AND** SHALL support --json output flag for machine-readable format

#### Scenario: Empty results
- **WHEN** no test cases match query
- **THEN** system SHALL display "No test cases found" message
- **AND** SHALL suggest running `tflow run` to generate tests

### Requirement: Support cross-project test reuse
The system SHALL enable finding and reusing test cases across different projects.

#### Scenario: Find reusable tests by pattern
- **WHEN** analyzing new project
- **THEN** system SHALL query database for VERIFIED test cases with matching patterns
- **AND** SHALL return tests sorted by reusability_score
- **AND** SHALL provide test code and selectors for adaptation

#### Scenario: Find reusable tests by tech stack
- **WHEN** project tech stack is detected
- **THEN** system SHALL query for test cases with matching tech_stack
- **AND** SHALL prioritize same-framework tests for higher reusability

### Requirement: Calculate reusability score
The system SHALL score test cases based on reuse potential.

#### Scenario: Reusability calculation
- **WHEN** calculating reusability score
- **THEN** system SHALL base score on: tech_stack match (30%), pattern match (30%), generic selectors (20%), VERIFIED status (10%), reuse_count (10%)
- **AND** SHALL return score between 0.0 and 1.0
- **AND** SHALL store score in reusability_score field

#### Scenario: Reuse count tracking
- **WHEN** test case is reused as template
- **THEN** system SHALL increment reuse_count in test_cases
- **AND** SHALL create record in reuse_links table documenting source and target

### Requirement: Manage test case lifecycle
The system SHALL support test case status transitions.

#### Scenario: Status transitions
- **WHEN** test case is created
- **THEN** system SHALL set status to DRAFT
- **WHEN** test case passes verification
- **THEN** system SHALL set status to VERIFIED
- **WHEN** test case fails verification
- **THEN** system SHALL set status to FAILED
- **WHEN** test case is replaced by better version
- **THEN** system MAY set status to DEPRECATED

### Requirement: Initialize database schema
The system SHALL create database tables on first run.

#### Scenario: Database initialization
- **WHEN** tflow runs for first time
- **THEN** system SHALL create data directory if not exists
- **AND** SHALL create SQLite database at data/e2e_tests.db
- **AND** SHALL execute schema for test_cases, test_runs, tools, case_tools tables
- **AND** SHALL create indexes for common queries

#### Scenario: Schema upgrade
- **WHEN** existing database has old schema
- **THEN** system SHALL detect schema version
- **AND** SHALL apply migration scripts to upgrade schema
- **AND** SHALL preserve existing data
