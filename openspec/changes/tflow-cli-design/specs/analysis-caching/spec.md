# Spec: Analysis Caching

Capability for caching project analysis results to reduce AI token usage on subsequent runs.

## ADDED Requirements

### Requirement: Calculate file hashes for change detection
The system SHALL calculate MD5 hashes of project source files to detect changes.

#### Scenario: Hash calculation
- **WHEN** scanning project files
- **THEN** system SHALL calculate MD5 hash for each source file
- **AND** SHALL include files with extensions: .vue, .tsx, .jsx, .ts, .js, .svelte
- **AND** SHALL exclude node_modules and dist directories
- **AND** SHALL store relative file paths as keys

#### Scenario: Hash comparison
- **WHEN** comparing current state to cached state
- **THEN** system SHALL identify new files (in current, not in cache)
- **AND** SHALL identify modified files (hash differs)
- **AND** SHALL identify deleted files (in cache, not in current)

### Requirement: Save analysis cache
The system SHALL persist analysis results to cache file after completion.

#### Scenario: Cache file creation
- **WHEN** project analysis completes
- **THEN** system SHALL create `.tflow/analysis-cache.json` in project directory
- **AND** SHALL include version, analyzed_at, project_name fields
- **AND** SHALL include tech_stack detection results
- **AND** SHALL include file_hashes object with all file paths and hashes
- **AND** SHALL include routes, api_calls, components arrays

#### Scenario: Cache structure validation
- **WHEN** saving cache file
- **THEN** system SHALL validate all required fields are present
- **AND** SHALL ensure file_hashes is not empty
- **AND** SHALL include cache version for future migration

### Requirement: Load existing cache
The system SHALL load cached analysis if available and valid.

#### Scenario: Cache loading
- **WHEN** cache file exists and is readable
- **THEN** system SHALL load and parse JSON from cache file
- **AND** SHALL validate cache structure
- **AND** SHALL return cache object if valid
- **AND** SHALL return null if cache is invalid or corrupted

#### Scenario: Cache version check
- **WHEN** loading cache with different version
- **THEN** system SHALL treat cache as invalid
- **AND** SHALL trigger full re-analysis
- **AND** SHALL display message about cache version mismatch

### Requirement: Perform incremental analysis
The system SHALL analyze only changed files when cache exists.

#### Scenario: No changes detected
- **WHEN** file hashes match cached hashes exactly
- **THEN** system SHALL skip analysis and use cached results
- **AND** SHALL display "✅ 无文件变更，使用缓存" message
- **AND** SHALL incur zero AI cost for analysis phase

#### Scenario: Few files changed
- **WHEN** 1-10 files have changed
- **THEN** system SHALL analyze only changed files incrementally
- **AND** SHALL merge new analysis results with existing cache
- **AND** SHALL display "🔄 发现 N 个文件变更，增量分析..." message
- **AND** SHALL save updated cache

#### Scenario: Many files changed
- **WHEN** more than 50% of files have changed
- **THEN** system MAY perform full re-analysis instead of incremental
- **AND** SHALL display message about major changes detected
- **AND** SHALL still save new cache after analysis

#### Scenario: First run (no cache)
- **WHEN** cache file does not exist
- **THEN** system SHALL perform full project analysis
- **AND** SHALL display "📊 首次分析，将全量扫描项目..." message
- **AND** SHALL save cache after analysis completes

### Requirement: Merge incremental analysis results
The system SHALL intelligently merge new analysis with cached data.

#### Scenario: Adding new route
- **WHEN** new route is detected in incremental analysis
- **THEN** system SHALL add route to routes array
- **AND** SHALL preserve existing routes
- **AND** SHALL re-sort routes by path if needed

#### Scenario: Removing deleted component
- **WHEN** component file is deleted
- **THEN** system SHALL remove component from components array
- **AND** SHALL flag routes using deleted component for review

#### Scenario: Updating API endpoint
- **WHEN** API call signature changes
- **THEN** system SHALL update api_calls entry with new signature
- **AND** SHALL preserve used_in references to components

### Requirement: Provide cache management commands
The system SHALL support manual cache operations.

#### Scenario: View cache status
- **WHEN** user runs `tflow cache status <project>`
- **THEN** system SHALL display cache age, analyzed file count
- **AND** SHALL list files changed since last analysis
- **AND** SHALL show cache size in KB

#### Scenario: Clear cache
- **WHEN** user runs `tflow cache clear <project>`
- **THEN** system SHALL delete cache file
- **AND** SHALL display confirmation message
- **AND** SHALL ensure next run performs full analysis

#### Scenario: Force re-analysis
- **WHEN** user runs `tflow plan` with `--no-cache` flag
- **THEN** system SHALL ignore existing cache
- **AND** SHALL perform full analysis regardless of changes
- **AND** SHALL overwrite cache with new results

### Requirement: Track analysis costs with and without cache
The system SHALL report cost savings from caching.

#### Scenario: Cost reporting
- **WHEN** analysis completes
- **THEN** system SHALL display AI token usage for analysis
- **AND** SHALL display estimated cost in USD
- **AND** SHALL show "使用缓存，节省 $X.XX" if cache was used
- **AND** SHALL include cost in final summary report

#### Scenario: Cost comparison
- **WHEN** showing cache status
- **THEN** system SHALL show estimated full analysis cost
- **AND** SHALL show actual cost with caching
- **AND** SHALL calculate percentage saved

### Requirement: Handle cache corruption
The system SHALL gracefully handle corrupted or invalid cache files.

#### Scenario: Corrupted cache detection
- **WHEN** cache file contains invalid JSON
- **THEN** system SHALL detect JSON parse error
- **AND** SHALL display "缓存文件损坏，重新分析" message
- **AND** SHALL perform full analysis
- **AND** SHALL backup corrupted cache file before overwriting

#### Scenario: Invalid cache structure
- **WHEN** cache JSON is valid but missing required fields
- **THEN** system SHALL detect missing fields
- **AND** SHALL treat cache as invalid
- **AND** SHALL perform full analysis

### Requirement: Support cache across project branches
The system SHALL handle cache when switching git branches.

#### Scenario: Branch-specific cache
- **WHEN** project is a git repository
- **THEN** system SHALL include current branch name in cache key
- **AND** SHALL maintain separate cache per branch
- **AND** SHALL auto-switch cache when branch changes

#### Scenario: Cache on non-git projects
- **WHEN** project is not a git repository
- **THEN** system SHALL use single cache for project
- **AND** SHALL still track file hashes for change detection

### Requirement: Cache expiry policy
The system SHALL implement reasonable cache expiry to prevent stale data.

#### Scenario: Time-based expiry
- **WHEN** cache is older than 7 days
- **THEN** system SHALL display cache age warning
- **AND** SHALL suggest running with --no-cache for fresh analysis
- **AND** SHALL still use cache unless user opts out

#### Scenario: Manual expiry control
- **WHEN** user wants to control cache duration
- **THEN** system SHALL support `--cache-ttl` flag (days)
- **AND** SHALL treat caches older than TTL as expired
