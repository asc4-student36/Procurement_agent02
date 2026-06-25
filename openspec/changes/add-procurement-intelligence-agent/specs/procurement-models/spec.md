## ADDED Requirements

### Requirement: Typed Procurement Request and Recommendation Models
The system SHALL define PurchaseRequest and ProcurementRecommendation as Pydantic v2 models with explicit typed fields and validation.

#### Scenario: Valid request model instance
- **WHEN** a purchase request payload contains all required fields with valid types
- **THEN** the payload is accepted as a valid PurchaseRequest model

### Requirement: Recommendation Decision Enumeration
The system SHALL constrain ProcurementRecommendation.decision to exactly one of approve, deny, or escalate.

#### Scenario: Invalid decision value rejected
- **WHEN** recommendation output contains any decision value outside approve, deny, or escalate
- **THEN** model validation fails and the value is rejected

### Requirement: Non-empty Recommendation Rationale
The system SHALL require ProcurementRecommendation.rationale to be non-empty.

#### Scenario: Empty rationale rejected
- **WHEN** recommendation output provides an empty rationale string
- **THEN** model validation fails and the output is rejected
