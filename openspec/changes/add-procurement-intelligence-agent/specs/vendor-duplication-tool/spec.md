## ADDED Requirements

### Requirement: Active Contract Conflict Detection
The system SHALL provide check_vendor_duplication that identifies active contracted vendors in the request category when the requested vendor is different.

#### Scenario: Conflicting contracted vendor exists
- **WHEN** request vendor differs from one or more active contracted vendors in the same category
- **THEN** check_vendor_duplication returns the conflicting vendor IDs

### Requirement: POL-001 Threshold Application
The system SHALL apply the POL-001 threshold of 25000 for single-source restriction evaluation in affected categories.

#### Scenario: Threshold-triggered duplication risk
- **WHEN** request amount exceeds 25000 in a POL-001 affected category and request vendor is non-contracted
- **THEN** check_vendor_duplication flags threshold-triggered conflict context for policy evaluation

### Requirement: No Conflict Reporting
The system SHALL return an explicit no-conflict result when no active contracted vendor conflict exists.

#### Scenario: No active duplicate contract
- **WHEN** request vendor is contracted for the category or no conflicting active contracted vendors exist
- **THEN** check_vendor_duplication reports no duplication conflict
