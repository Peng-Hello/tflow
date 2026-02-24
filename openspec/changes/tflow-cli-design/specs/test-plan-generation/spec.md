# Spec: Test Plan Generation

Capability for generating structured test plans identifying user interaction paths with priority levels and step-by-step scenarios.

## ADDED Requirements

### Requirement: Infer core user interaction paths
The system SHALL analyze the project structure and API usage to infer critical user interaction paths prioritized by business importance.

#### Scenario: P0 authentication flow identification
- **WHEN** login page and auth flow are detected
- **THEN** system SHALL generate AUTH_FLOW test case with priority P0
- **AND** SHALL include steps: navigate to login, enter credentials, submit, verify redirect
- **AND** SHALL include positive and negative test scenarios

#### Scenario: P0 business flow identification
- **WHEN** critical business operations are detected (e.g., payment, data submission)
- **THEN** system SHALL generate corresponding test case with priority P0
- **AND** SHALL identify all steps in the business process
- **AND** SHALL include validation assertions for each step

#### Scenario: P1 CRUD operation identification
- **WHEN** list, create, edit, delete components are detected
- **THEN** system SHALL generate CRUD_FLOW test case with priority P1
- **AND** SHALL include steps for each CRUD operation
- **AND** SHALL verify data persistence after each operation

### Requirement: Prioritize test scenarios
The system SHALL assign priority levels (P0, P1, P2) based on business criticality and usage frequency.

#### Scenario: Priority assignment logic
- **WHEN** assigning priorities to test cases
- **THEN** system SHALL assign P0 to authentication and critical business flows
- **AND** SHALL assign P1 to CRUD operations and navigation
- **AND** SHALL assign P2 to settings, help pages, and edge cases

#### Scenario: User-configurable priority filtering
- **WHEN** user specifies --priority flag
- **THEN** system SHALL only generate test cases matching specified priorities
- **AND** SHALL support comma-separated priority list (e.g., "P0,P1")

### Requirement: Match reusable test patterns
The system SHALL match detected scenarios to reusable test patterns for faster generation.

#### Scenario: AUTH_FLOW pattern matching
- **WHEN** login/auth flow is detected
- **THEN** system SHALL match to AUTH_FLOW pattern
- **AND** SHALL check database for existing VERIFIED AUTH_FLOW tests
- **AND** SHALL reuse test structure with adapted selectors and URLs

#### Scenario: CRUD_FLOW pattern matching
- **WHEN** list/create/edit/delete operations are detected
- **THEN** system SHALL match to CRUD_FLOW pattern
- **AND** SHALL check database for existing VERIFIED CRUD_FLOW tests
- **AND** SHALL identify if same tech stack for higher reusability

#### Scenario: DATA_SYNC pattern matching
- **WHEN** cross-system data synchronization is detected
- **THEN** system SHALL match to DATA_SYNC pattern
- **AND** SHALL identify external tools needed for validation
- **AND** SHALL structure test with before/after tool calls

### Requirement: Generate editable test plan document
The system SHALL generate a Markdown test plan file for human review and modification.

#### Scenario: Test plan structure
- **WHEN** generating test plan with `tflow plan` command
- **THEN** system SHALL create Markdown file at `<project>/.tflow/e2e-test-plan.md`
- **AND** SHALL include project metadata (tech stack, generated time)
- **AND** SHALL list all test cases with priority and pattern
- **AND** SHALL include step-by-step test scenarios in table format

#### Scenario: Test plan editability
- **WHEN** test plan is generated
- **THEN** system SHALL include user comment sections for feedback
- **AND** SHALL support marking test cases as "skip" by changing status
- **AND** SHALL allow users to add, remove, or modify test steps
- **AND** SHALL provide editing instructions in plan footer

#### Scenario: Test plan execution
- **WHEN** running `tflow run --from-plan` with edited plan
- **THEN** system SHALL read plan file and respect modifications
- **AND** SHALL skip test cases marked with skip status
- **AND** SHALL generate code according to modified steps
- **AND** SHALL consider user comments in prompt

### Requirement: Integrate external tools into test plan
The system SHALL identify when test scenarios require external tools and include them in the plan.

#### Scenario: External tool identification
- **WHEN** test scenario involves cross-system validation
- **THEN** system SHALL identify required tools from registered tools
- **AND** SHALL mark test case with associated tool names
- **AND** SHALL include tool call steps in test scenario (before/after/verify phases)

#### Scenario: Tool parameter inference
- **WHEN** tool requires parameters
- **THEN** system SHALL infer appropriate parameters from code context
- **AND** SHALL use params_schema to validate parameter choices
- **AND** SHALL include parameters in test plan tool call steps

### Requirement: Generate test summary metadata
The system SHALL output structured metadata about generated test plans.

#### Scenario: JSON summary output
- **WHEN** test plan generation is complete
- **THEN** system SHALL output JSON with test metadata
- **AND** SHALL include tests array with name, pattern, file path
- **AND** SHALL include total count by priority level
- **AND** SHALL include list of associated tools if any

#### Scenario: Analysis reuse reporting
- **WHEN** existing test cases are reused
- **THEN** system SHALL report reused test source (project:case_id)
- **AND** SHALL calculate reusability score
- **AND** SHALL indicate which test cases are adaptations vs. new
