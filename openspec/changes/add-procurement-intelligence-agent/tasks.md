## 1. Models and Data Access

- [ ] 1.1 Implement PurchaseRequest and ProcurementRecommendation in models.py using Pydantic v2
- [ ] 1.2 Constrain recommendation decision to approve, deny, or escalate
- [ ] 1.3 Enforce non-empty recommendation rationale validation
- [ ] 1.4 Implement data loader utilities in data/loader.py for budgets, vendors, policies, and requests
- [ ] 1.5 Add tests for model validation and loader error handling

## 2. Tool Implementation

- [ ] 2.1 Implement check_budget in tools/budget.py with within_budget, remaining_budget, and overage outputs
- [ ] 2.2 Implement check_vendor_duplication in tools/vendor_duplication.py with POL-001 threshold behavior
- [ ] 2.3 Implement check_policy_compliance in tools/policy_compliance.py with structured violation output
- [ ] 2.4 Implement assess_risk in tools/risk_assessment.py with compliance_flag, contract_status, and risk_level
- [ ] 2.5 Add primary success-path tests for each tool in tests/
- [ ] 2.6 Add unknown cost center and unknown vendor edge-case tests

## 3. Agent Orchestration and Decision Logic

- [ ] 3.1 Implement procurement agent wiring in agent.py using pydantic-ai with output_type=ProcurementRecommendation
- [ ] 3.2 Orchestrate calls to all four tools for each request
- [ ] 3.3 Implement deterministic decision precedence escalate > deny > approve
- [ ] 3.4 Implement rationale synthesis that references driving check findings
- [ ] 3.5 Catch tool errors and surface them in rationale with safe fallback behavior

## 4. End-to-End Verification and Compliance

- [ ] 4.1 Add integration tests covering approve, deny, and escalate sample outcomes
- [ ] 4.2 Run openspec validate add-procurement-intelligence-agent and resolve validation issues
- [ ] 4.3 Run pytest tests/ -v --tb=short --junitxml=docs/test-results.xml
- [ ] 4.4 Update docs/test-results.xml and backoutPlan.md per RAPID controls before review
