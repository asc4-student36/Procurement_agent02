## Context

The procurement workflow requires a consistent pre-screen of purchase requests before human review. Current data is provided through mock datasets for budgets, vendors, policies, and sample requests, and the project conventions require all access through data/loader.py. The solution must produce structured recommendations (approve, deny, escalate) with explainable rationale while remaining robust when tools fail.

## Goals / Non-Goals

**Goals:**
- Define an architecture for a Pydantic AI agent that accepts a typed PurchaseRequest and returns a typed ProcurementRecommendation.
- Standardize tool orchestration across four checks: budget, vendor duplication, policy compliance, and risk assessment.
- Enforce decision precedence of escalate > deny > approve.
- Ensure tool failures are caught and surfaced in rationale output instead of causing crashes.
- Keep data loading centralized in data/loader.py and avoid direct reads from mock_data/ in tools and agent logic.

**Non-Goals:**
- Introduce new procurement policies beyond the provided mock policy set.
- Implement live integrations to external ERP, contract, or compliance systems.
- Replace human procurement approval authority.

## Decisions

### 1) Typed model boundary with Pydantic v2 and Pydantic AI output contract
The agent input and output will be explicitly modeled with PurchaseRequest and ProcurementRecommendation, and recommendation decision values will be constrained to approve, deny, or escalate.
Rationale: strict contracts prevent ambiguous output and align with acceptance criteria.
Alternative considered: untyped dict I/O; rejected due to weaker validation and less reliable downstream automation.

### 2) Centralized data access in data/loader.py
All tools will retrieve budgets, vendors, and policies through loader functions rather than reading mock files directly.
Rationale: single access path improves testability and enforces project governance.
Alternative considered: each tool reads JSON directly; rejected due to duplication and violation of conventions.

### 3) Tool-per-check architecture with explicit result payloads
Each required check maps to one tool function:
- check_budget
- check_vendor_duplication
- check_policy_compliance
- assess_risk
Each tool returns structured fields needed for recommendation synthesis.
Rationale: modular checks are easier to test independently and align to user stories US-001 through US-004.
Alternative considered: single monolithic evaluator; rejected due to poor separation of concerns and reduced test clarity.

### 4) Deterministic recommendation synthesis using precedence
Final recommendation is computed by evaluating all check outputs and applying precedence rules:
1. If any check requests escalation, final decision is escalate.
2. Else if any check requests denial, final decision is deny.
3. Else final decision is approve.
Rationale: deterministic conflict resolution is required when checks disagree.
Alternative considered: deny precedence over escalate; rejected because governance requires flagged/high-risk cases to route for review.

### 5) Error-to-rationale fallback strategy
Tool invocations are wrapped with exception handling. Any tool error is appended to rationale and mapped to escalate unless a stricter forced decision is already present.
Rationale: prevents silent failure and preserves explainability under partial outages.
Alternative considered: fail-fast on tool error; rejected because it violates the requirement to return advisory output without crashing.

## Risks / Trade-offs

- Risk: Policy text and sample outcomes may contain edge-case ambiguity. -> Mitigation: document precedence and encode forced decision semantics in policy compliance output.
- Risk: Over-escalation if error handling is too conservative. -> Mitigation: limit escalation-on-error to affected checks and include explicit rationale messages.
- Risk: Divergence between vendor duplication and policy compliance logic. -> Mitigation: define ownership boundaries (duplication detects conflicts; policy tool applies formal policy violations).
- Risk: Missing approval metadata for manager/director thresholds in sample requests. -> Mitigation: treat threshold findings as compliance signals and include them in rationale while preserving precedence.

## Migration Plan

1. Create models and loader interfaces.
2. Implement and unit test each tool independently.
3. Implement agent orchestration and deterministic recommendation synthesis.
4. Add integration tests against sample requests to verify approve/deny/escalate coverage.
5. Run openspec validate and pytest test capture.

Rollback approach:
- Revert to prior baseline commit if recommendation synthesis or tool integration introduces regressions.
- Use backoutPlan.md to follow documented revert owner and steps.

## Open Questions

- For budget overage edge cases that are near approval thresholds, should policy force deny or allow explicit escalation exception?
- Should policy compliance or risk assessment own the contract-status denial semantics for expired vendors?
- What is the exact rationale template format expected for showcase consistency?
