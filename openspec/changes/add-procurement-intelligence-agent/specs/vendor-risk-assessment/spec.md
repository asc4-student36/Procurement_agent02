## ADDED Requirements

### Requirement: Vendor Risk Signal Assessment
The system SHALL provide assess_risk that returns compliance_flag, contract_status, and a computed risk_level for the requested vendor.

#### Scenario: Vendor risk assessed
- **WHEN** a request references a known vendor
- **THEN** assess_risk returns compliance_flag, contract_status, and risk_level

### Requirement: Risk Level Domain
The system SHALL constrain risk_level to low, medium, high, or critical.

#### Scenario: Invalid risk level prevented
- **WHEN** risk evaluation produces a value outside low, medium, high, or critical
- **THEN** validation fails and the result is rejected

### Requirement: Unknown Vendor Handling
The system SHALL return a structured error for unknown vendor IDs.

#### Scenario: Vendor missing from dataset
- **WHEN** request vendor_id does not exist in vendor data
- **THEN** assess_risk returns structured error context without unhandled exception
