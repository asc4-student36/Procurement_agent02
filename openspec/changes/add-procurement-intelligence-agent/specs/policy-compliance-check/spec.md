## ADDED Requirements

### Requirement: Full Policy Set Evaluation
The system SHALL provide check_policy_compliance that evaluates a request against all policies defined in the policy dataset.

#### Scenario: Policy set checked
- **WHEN** a purchase request is evaluated for compliance
- **THEN** check_policy_compliance processes all policy records and returns matched findings

### Requirement: Structured Violation Reporting
The system SHALL return policy violations with policy_id, rule description, and forced decision.

#### Scenario: Policy violation detected
- **WHEN** one or more policies are violated
- **THEN** check_policy_compliance returns a structured list of violations with forced decision values

### Requirement: Policy Result for Compliant Requests
The system SHALL return an explicit compliant result when no policy violations are detected.

#### Scenario: No policy violation
- **WHEN** no policy condition is violated by the request
- **THEN** check_policy_compliance reports compliant status with an empty violations list
