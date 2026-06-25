## ADDED Requirements

### Requirement: Centralized Mock Data Access
The system SHALL load mock procurement datasets through data/loader.py and SHALL NOT read files in mock_data/ directly from tool or agent logic.

#### Scenario: Tool obtains budgets via loader
- **WHEN** a tool needs budget data
- **THEN** it retrieves data through data/loader.py interfaces rather than direct file I/O

### Requirement: Loader Error Propagation
The system SHALL surface loader failures to calling components with structured error context.

#### Scenario: Missing data source
- **WHEN** a requested dataset cannot be loaded
- **THEN** loader returns a structured error that the caller can include in rationale
