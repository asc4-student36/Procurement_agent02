## Why

FedEx procurement teams need consistent, explainable pre-screening of purchase requests so analysts can focus on high-risk and high-value decisions. This change is needed now to establish a reliable advisory workflow that produces structured recommendations aligned with policy and budget controls.

## What Changes

- Introduce a Pydantic AI procurement agent that accepts a purchase request and returns a structured recommendation.
- Enforce typed input and output contracts using Pydantic v2 models: PurchaseRequest and ProcurementRecommendation.
- Constrain recommendation decision values to approve, deny, or escalate, and require a non-empty rationale.
- Add tool-driven screening flow that calls four checks: budget, vendor duplication, policy compliance, and vendor risk.
- Require mock data access through data/loader.py only; tool and agent logic must not read files in mock_data directly.
- Define decision precedence as escalate > deny > approve when combining check results.
- Require tool failures to be caught and surfaced in the rationale instead of causing unhandled failures.

## Capabilities

### New Capabilities
- `procurement-models`: Define and validate PurchaseRequest and ProcurementRecommendation with strict decision constraints.
- `procurement-data-loader`: Provide centralized, typed loading of mock procurement data via data/loader.py.
- `budget-check`: Evaluate request amount against cost center remaining budget and return overage context.
- `vendor-duplication-check`: Detect contracted-vendor conflicts for category and threshold scenarios.
- `policy-compliance-check`: Evaluate request against procurement policies and return violations with forced outcomes.
- `vendor-risk-assessment`: Assess vendor compliance and contract risk signals for decision support.
- `procurement-recommendation-agent`: Orchestrate the four checks and produce final approve/deny/escalate recommendation with rationale using precedence rules.

### Modified Capabilities
- None.

## Impact

- Affected code: models.py, data/loader.py, tools/, agent.py, tests/.
- APIs/contracts: standardizes the recommendation output schema and accepted decision enum.
- Dependencies: uses pydantic-ai for agent orchestration and Pydantic v2 for schema validation.
- Systems/process: introduces deterministic pre-screening behavior and explicit error-to-rationale handling for reliability.
