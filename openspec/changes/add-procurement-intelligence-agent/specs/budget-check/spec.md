## ADDED Requirements

### Requirement: Budget Evaluation by Cost Center
The system SHALL provide check_budget that evaluates request total_amount against the remaining quarterly budget for the request cost center.

#### Scenario: Request within remaining budget
- **WHEN** total_amount is less than or equal to remaining budget
- **THEN** check_budget reports within_budget as true and overage as 0

### Requirement: Budget Overage Reporting
The system SHALL compute and return overage amount when request total_amount exceeds remaining budget.

#### Scenario: Request exceeds remaining budget
- **WHEN** total_amount is greater than remaining budget
- **THEN** check_budget reports within_budget as false and overage as total_amount minus remaining budget

### Requirement: Unknown Cost Center Handling
The system SHALL return a structured error when the request cost center is not found.

#### Scenario: Cost center does not exist
- **WHEN** the request cost_center_id has no matching budget record
- **THEN** check_budget returns a structured error result instead of raising an unhandled exception
