# Spec: Dev Server Lifecycle

Capability for automatically starting and stopping project development servers during test execution.

## ADDED Requirements

### Requirement: Start development server automatically
The system SHALL start the project's development server before test execution.

#### Scenario: Default npm start
- **WHEN** no server command is specified
- **THEN** system SHALL execute `npm run dev` in project directory
- **AND** SHALL capture server process for later termination
- **AND** SHALL wait for server to be ready before proceeding

#### Scenario: Custom server command
- **WHEN** project config specifies `server-cmd` in `.tflow.json`
- **THEN** system SHALL use specified command (e.g., `yarn dev`, `pnpm dev`)
- **AND** SHALL execute command in project directory

#### Scenario: Server already running
- **WHEN** user provides `--server-url http://localhost:3000` flag
- **THEN** system SHALL skip server start
- **AND** SHALL use provided URL for tests
- **AND** SHALL display "使用已有服务器: <url>" message

### Requirement: Detect free port automatically
The system SHALL find an available port if configured port is in use.

#### Scenario: Auto port detection
- **WHEN** starting development server
- **THEN** system SHALL find free port using socket.bind(("", 0"))
- **AND** SHALL set PORT environment variable to detected port
- **AND** SHALL pass port to server process via environment

#### Scenario: Port conflict handling
- **WHEN** project config specifies `server-port` that is in use
- **THEN** system SHALL detect port is unavailable
- **AND** SHALL find alternative free port
- **AND** SHALL display actual port used in message

#### Scenario: Explicit port override
- **WHEN** user wants specific port
- **THEN** system SHALL respect `server-port` from config
- **AND** SHALL not override if port is available
- **AND** SHALL fail if port is unavailable (not auto-find)

### Requirement: Wait for server readiness
The system SHALL wait for server to be ready before proceeding with tests.

#### Scenario: Health check polling
- **WHEN** server process is started
- **THEN** system SHALL poll server port every 1 second
- **AND** SHALL check if port is accepting connections
- **AND** SHALL consider server ready when port responds
- **AND** SHALL timeout after 30 seconds with error

#### Scenario: Ready message detection
- **WHEN** server outputs ready message (e.g., "ready on", "listening")
- **THEN** system SHALL detect ready message in stdout
- **AND** SHALL mark server as ready
- **AND** SHALL proceed to test execution

#### Scenario: Server startup timeout
- **WHEN** server does not become ready within 30 seconds
- **THEN** system SHALL terminate server process
- **AND** SHALL raise TimeoutError with diagnostics
- **AND** SHALL include last 20 lines of server output in error

### Requirement: Stop server after tests complete
The system SHALL cleanly shut down development server after test execution.

#### Scenario: Clean shutdown
- **WHEN** tests complete (success or failure)
- **THEN** system SHALL call process.terminate() on server
- **AND** SHALL wait up to 5 seconds for graceful shutdown
- **AND** SHALL display "🛑 开发服务器已停止" message

#### Scenario: Force kill if needed
- **WHEN** server doesn't respond to terminate() within 5 seconds
- **THEN** system SHALL call process.kill() to force terminate
- **AND** SHALL display warning about force kill

#### Scenario: Shutdown in error cases
- **WHEN** test execution fails with exception
- **THEN** system SHALL still attempt server shutdown in finally block
- **AND** SHALL ensure server is always stopped

### Requirement: Capture server output
The system SHALL capture and handle server stdout/stderr for debugging.

#### Scenario: Output capture
- **WHEN** server is running
- **THEN** system SHALL capture stdout and stderr pipes
- **AND** SHALL not display server output during normal operation
- **AND** SHALL save output to buffer for error diagnostics

#### Scenario: Verbose mode output
- **WHEN** --verbose flag is set
- **THEN** system SHALL display server output in real-time
- **AND** SHALL prefix server lines with [SERVER] tag
- **AND** SHALL include both stdout and stderr

#### Scenario: Output on error
- **WHEN** server fails to start or times out
- **THEN** system SHALL include captured server output in error message
- **AND** SHALL show last 20 lines of output for context

### Requirement: Handle server configuration files
The system SHALL respect project-specific server configuration.

#### Scenario: Vite config detection
- **WHEN** project has `vite.config.ts`
- **THEN** system SHALL read server port from config if specified
- **AND** SHALL use detected port as default (fallback to auto-detect)

#### Scenario: Next.js config detection
- **WHEN** project is Next.js with `next.config.js`
- **THEN** system SHALL use `npm run dev` as default command
- **AND** SHALL respect port configured in next.config.js

#### Scenario: Custom server scripts
- **WHEN** package.json has custom dev script
- **THEN** system SHALL use the script defined in package.json
- **AND** SHALL not override custom scripts

### Requirement: Support --no-server flag
The system SHALL allow users to skip server management entirely.

#### Scenario: Manual server management
- **WHEN** user provides `--no-server` flag
- **THEN** system SHALL not start or stop any server
- **AND** SHALL assume server is already running
- **AND** SHALL require `--server-url` to be provided

#### Scenario: No-server error handling
- **WHEN** --no-server is used without --server-url
- **THEN** system SHALL raise error requiring --server-url
- **AND** SHALL provide helpful error message

### Requirement: Track server process state
The system SHALL maintain server process state throughout execution.

#### Scenario: Process tracking
- **WHEN** server is started
- **THEN** system SHALL store process object in DevServer class
- **AND** SHALL track process PID
- **AND** SHALL track server URL for test usage

#### Scenario: Status checking
- **WHEN** server is running
- **THEN** system SHALL provide is_running() method
- **AND** SHALL return True if process is alive
- **AND** SHALL return False if process has terminated

### Requirement: Handle server crashes during tests
The system SHALL detect and handle server crashes during test execution.

#### Scenario: Crash detection
- **WHEN** server process terminates while tests are running
- **THEN** system SHALL detect process exit via poll
- **AND** SHALL abort test execution
- **AND** SHALL report server crash with exit code

#### Scenario: Auto-restart on crash
- **WHEN** server crashes during test run
- **THEN** system MAY attempt to restart server once
- **AND** SHALL wait for server to be ready again
- **AND** SHALL continue or abort tests based on retry configuration

### Requirement: Support multiple server instances
The system SHALL handle scenarios requiring multiple servers (e.g., frontend + backend).

#### Scenario: Single server (default)
- **WHEN** running tflow on typical project
- **THEN** system SHALL start single dev server
- **AND** SHALL use this server for all tests

#### Scenario: Multiple server configuration
- **WHEN** project config specifies multiple servers
- **THEN** system SHALL support `servers` array in `.tflow.json`
- **AND** SHALL start each server with unique port
- **AND** SHALL provide environment variables for server URLs
- **AND** SHALL stop all servers after tests complete
