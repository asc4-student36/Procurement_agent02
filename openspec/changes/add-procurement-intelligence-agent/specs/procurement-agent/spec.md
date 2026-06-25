## ADDED Requirements

### Requirement: Agent Input and Output Type Contract
The system SHALL define the procurement agent to accept input validated as PurchaseRequest and return output validated as ProcurementRecommendation from models.py.

#### Scenario: Valid typed recommendation returned
- **WHEN** the agent receives a valid PurchaseRequest
- **THEN** the agent returns a ProcurementRecommendation with request_id, decision, and non-empty rationale

### Requirement: Four-Tool Evaluation Workflow
The system SHALL evaluate each request using all four tools: check_budget, check_vendor_duplication, check_policy_compliance, and assess_risk.

#### Scenario: All tools executed for a request
- **WHEN** the agent evaluates a PurchaseRequest
- **THEN** the agent invokes all four tools and uses their results in decision synthesis

### Requirement: Decision Priority Precedence
The system SHALL apply recommendation precedence as escalate over deny over approve when multiple checks produce competing outcomes.

#### Scenario: Escalate and deny signals both present
- **WHEN** at least one check produces escalate and another produces deny
- **THEN** the final recommendation decision is escalate

### Requirement: Structured Error Handling and Safe Fallback
The system SHALL catch tool or orchestration errors, include the failure context in rationale, and return a structured recommendation rather than failing silently.

#### Scenario: Tool failure during evaluation
- **WHEN** any tool raises an exception or returns an error payload
- **THEN** the agent returns a ProcurementRecommendation with non-empty rationale containing the error context and a safe decision consistent with precedence rules

### Requirement: System Prompt Behavioral Constraints
The system SHALL constrain agent behavior through a system prompt that requires structured output, full four-check evaluation, evidence-based rationale, and allowed decision values only.

#### Scenario: Prompt-constrained output generation
- **WHEN** the agent generates a recommendation
- **THEN** the output is limited to decision values approve, deny, or escalate and includes rationale citing relevant findings from tool outputs
