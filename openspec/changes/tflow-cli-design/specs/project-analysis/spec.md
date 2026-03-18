# Spec: Project Analysis

Capability for analyzing frontend project structure to detect framework, extract routes, identify components and API endpoints.

## ADDED Requirements

### Requirement: Detect frontend framework and tech stack
The system SHALL automatically detect the frontend framework, UI library, router, and state management solution by analyzing package.json, build configuration, and source code patterns.

#### Scenario: Vue 3 project detection
- **WHEN** analyzing a project with `vue` in devDependencies and `.vue` files
- **THEN** system SHALL detect framework as "Vue 3"
- **AND** SHALL detect Vue Router if router configuration file exists
- **AND** SHALL detect Pinia if pinia dependencies present

#### Scenario: React project detection
- **WHEN** analyzing a project with `react` in dependencies
- **THEN** system SHALL detect framework as "React"
- **AND** SHALL detect React Router if react-router dependencies present
- **AND** SHALL detect state management (Redux, Zustand, Context) if patterns found

#### Scenario: Angular project detection
- **WHEN** analyzing a project with `@angular/core` in dependencies
- **THEN** system SHALL detect framework as "Angular"
- **AND** SHALL detect Angular Router from routing module files

### Requirement: Extract application routes
The system SHALL extract all application routes from router configuration files, including path, component name, and authentication requirements.

#### Scenario: Vue Router extraction
- **WHEN** analyzing Vue project with router configuration
- **THEN** system SHALL extract routes from `src/router/index.ts` or similar
- **AND** SHALL identify path patterns (e.g., `/login`, `/users/:id`)
- **AND** SHALL map paths to component files
- **AND** SHALL detect route meta fields for auth requirements

#### Scenario: React Router extraction
- **WHEN** analyzing React project with react-router
- **THEN** system SHALL extract routes from `<Route>` components in app entry
- **AND** SHALL identify path and element/component mappings
- **AND** SHALL detect nested route structures

### Requirement: Identify interactive components
The system SHALL identify interactive UI components including forms, modals, tables, and buttons with their test selectors.

#### Scenario: Form component identification
- **WHEN** analyzing component files with form patterns
- **THEN** system SHALL identify form components
- **AND** SHALL extract input fields with `data-testid` attributes
- **AND** SHALL identify submit buttons and validation elements

#### Scenario: Table component identification
- **WHEN** analyzing components with table/grid patterns
- **THEN** system SHALL identify table components
- **AND** SHALL extract column definitions
- **AND** SHALL identify action buttons (edit, delete) within table rows

### Requirement: Extract API endpoint usage
The system SHALL extract all API endpoints called from the frontend codebase, including method, URL pattern, and usage location.

#### Scenario: REST API extraction
- **WHEN** analyzing JavaScript/TypeScript files with fetch or axios calls
- **THEN** system SHALL extract HTTP method (GET, POST, PUT, DELETE)
- **AND** SHALL extract URL patterns
- **AND** SHALL map endpoints to components that use them

#### Scenario: API client identification
- **WHEN** analyzing project with centralized API client
- **THEN** system SHALL identify API client configuration
- **AND** SHALL extract base URL and authentication headers
- **AND** SHALL identify all endpoint definitions

### Requirement: Detect authentication flow
The system SHALL identify authentication-related components and flows including login forms, token storage, and protected routes.

#### Scenario: Login flow detection
- **WHEN** analyzing project with authentication
- **THEN** system SHALL identify login page component
- **AND** SHALL extract login form fields (username, password)
- **AND** SHALL identify token storage mechanism (localStorage, cookie)
- **AND** SHALL detect authentication guards/redirects

#### Scenario: Protected route detection
- **WHEN** analyzing routes with auth requirements
- **THEN** system SHALL mark routes requiring authentication
- **AND** SHALL identify auth guard implementation
- **AND** SHALL detect unauthorized redirect behavior

### Requirement: Generate structured analysis report
The system SHALL output a structured JSON report containing all detected project information.

#### Scenario: Complete analysis output
- **WHEN** project analysis is complete
- **THEN** system SHALL output JSON with tech_stack object
- **AND** SHALL include routes array with path, component, auth_required
- **AND** SHALL include api_endpoints array with method, path, used_in
- **AND** SHALL include interactive_elements object with forms, modals, tables
- **AND** SHALL include authentication flow details

#### Scenario: Analysis with confidence scores
- **WHEN** detection patterns have uncertainty
- **THEN** system SHALL include confidence scores for uncertain detections
- **AND** SHALL mark detections with confidence below 0.7 as "tentative"
