## ADDED Requirements

### Requirement: Tool-Orchestrated Recommendation Flow
The system SHALL run budget, vendor duplication, policy compliance, and risk assessment checks for each purchase request before producing a recommendation.

#### Scenario: All checks executed
- **WHEN** the agent receives a valid PurchaseRequest
- **THEN** it executes all four checks and uses their outputs to form a recommendation

### Requirement: Decision Precedence
The system SHALL apply precedence of escalate over deny over approve when multiple check outcomes apply.

#### Scenario: Escalate and deny both present
- **WHEN** at least one check indicates escalation and another indicates denial
- **THEN** final recommendation decision is escalate

### Requirement: Explainable Rationale Synthesis
The system SHALL generate a non-empty rationale that references the findings from checks that influenced the final decision.

#### Scenario: Recommendation produced
- **WHEN** final decision is produced
- **THEN** rationale includes the key finding(s) that caused approve, deny, or escalate

### Requirement: Tool Error Resilience
The system SHALL catch tool exceptions and include error context in rationale instead of returning an unhandled failure.

#### Scenario: Tool execution fails
- **WHEN** any check tool raises an exception
- **THEN** the agent returns a structured recommendation with error details reflected in rationale
