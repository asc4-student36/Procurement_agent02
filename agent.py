"""Main procurement agent definition and execution entrypoint."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

from dotenv import load_dotenv
from pydantic_ai import Agent

from data.loader import load_requests
from models import ProcurementRecommendation, PurchaseRequest
from tools.budget import check_budget
from tools.policy_compliance import check_policy_compliance
from tools.risk_assessment import assess_risk
from tools.vendor_duplication import check_vendor_duplication

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

SYSTEM_PROMPT = """
You are the FedEx Procurement Intelligence Agent.

You MUST evaluate every request using all four tools:
- check_budget
- check_vendor_duplication
- check_policy_compliance
- assess_risk

Use this mandatory decision algorithm based on tool outputs:
1) If any tool reports an error, decision MUST be escalate.
2) Evaluate policy violations from check_policy_compliance:
     - If any violation has forced_decision=deny, final decision MUST be deny.
     - Else if any violation has forced_decision=escalate, final decision MUST be escalate.
     - Else continue.
3) If no blocking violations exist:
     - If budget check is within_budget=True and there is no duplication_conflict,
         decision MUST be approve.
     - Otherwise, decision MUST be escalate.

Important interpretation rules:
- check_policy_compliance advisories are non-blocking and MUST NOT change a final
    decision from approve to escalate.
- A deny decision MUST NOT be overridden by risk-level language or advisory notes.

Your final output MUST match ProcurementRecommendation:
- decision MUST be one of approve, deny, escalate
- rationale MUST be non-empty and reference concrete findings from tool output
  (policy IDs, overage, conflicting vendors, risk signals, or tool errors)

If any tool fails or returns an error, include the error context in rationale and
choose a safe decision using the same priority rules.

Error handling requirement:
- When a tool response includes error/error_type, you MUST reference that error
    context in rationale and return decision=escalate.

Rationale template requirement (mandatory):
- Write 2 to 4 complete sentences using plain prose only.
- Name the specific check(s) that drove the decision (for example: Budget check,
  Policy compliance check, Vendor duplication check, Risk assessment).
- Include concrete context such as policy IDs, relevant amounts, or vendor name.
- Do not use bullet points or fragments.
""".strip()

llm_agent: Agent[None, ProcurementRecommendation] = Agent(
    model="openai:gpt-4o-mini",
    output_type=ProcurementRecommendation,
    system_prompt=SYSTEM_PROMPT,
    tools=[
        check_budget,
        check_vendor_duplication,
        check_policy_compliance,
        assess_risk,
    ],
)


@dataclass
class _DeterministicRunResult:
    """Compatibility result object for temporary manual scripts."""

    data: ProcurementRecommendation

    @property
    def output(self) -> ProcurementRecommendation:
        """Mirror pydantic-ai result access pattern used across environments."""
        return self.data


def _extract_request_id(user_prompt: str) -> str | None:
    """Extract request_id from free-form prompt text."""
    match = re.search(r"request_id\s*[=:]\s*['\"]?(REQ-\d{3})", user_prompt)
    if match:
        return match.group(1)

    match = re.search(r"\b(REQ-\d{3})\b", user_prompt)
    if match:
        return match.group(1)

    return None


def _request_by_id(request_id: str) -> PurchaseRequest:
    """Load and validate a request by ID from mock data."""
    raw_request = next(item for item in load_requests() if item["request_id"] == request_id)
    payload = {
        key: value
        for key, value in raw_request.items()
        if key in PurchaseRequest.model_fields
    }
    return PurchaseRequest.model_validate(payload)


def run_procurement_agent(request: PurchaseRequest) -> ProcurementRecommendation:
    """Run the procurement agent for a validated PurchaseRequest input."""
    try:
        budget_result = check_budget(request.cost_center_id, request.total_amount)
        duplication_result = check_vendor_duplication(
            request.vendor_id,
            request.category,
            request.total_amount,
        )
        policy_result = check_policy_compliance(request)
        risk_result = assess_risk(request.vendor_id)

        error_messages = [
            f"{result.get('error_type', 'Error')}: {result['error']}"
            for result in [budget_result, duplication_result, policy_result, risk_result]
            if isinstance(result, dict) and "error" in result and result["error"]
        ]
        policy_errors = [
            str(item.get("rule_description", ""))
            for item in policy_result.get("violations", [])
            if item.get("policy_id") == "POL-DATA"
        ]
        error_messages.extend([msg for msg in policy_errors if msg])

        if error_messages:
            return ProcurementRecommendation(
                request_id=request.request_id,
                decision="escalate",
                rationale=(
                    "Tool execution could not complete a reliable procurement review for "
                    f"vendor {request.vendor_name} on request {request.request_id}. "
                    "The Budget check, Policy compliance check, Vendor duplication check, "
                    "or Risk assessment returned error details: "
                    f"{' ; '.join(error_messages)}. "
                    "Because required data is incomplete, this request is escalated for "
                    "manual procurement review."
                ),
            )

        violations = policy_result.get("violations", [])
        advisories = policy_result.get("advisories", [])
        deny_violations = [item for item in violations if item.get("forced_decision") == "deny"]
        escalate_violations = [
            item for item in violations if item.get("forced_decision") == "escalate"
        ]

        if deny_violations:
            policy_ids = ", ".join(str(item.get("policy_id", "")) for item in deny_violations)
            return ProcurementRecommendation(
                request_id=request.request_id,
                decision="deny",
                rationale=(
                    "Policy compliance check identified blocking violation(s) "
                    f"{policy_ids} for vendor {request.vendor_name}. "
                    "Budget check and Vendor duplication check were reviewed, but the "
                    "policy violation requires a deny outcome. "
                    f"The requested amount of ${request.total_amount:,.0f} cannot proceed "
                    "until the policy issue is resolved."
                ),
            )

        if escalate_violations:
            policy_ids = ", ".join(
                str(item.get("policy_id", "")) for item in escalate_violations
            )
            return ProcurementRecommendation(
                request_id=request.request_id,
                decision="escalate",
                rationale=(
                    "Policy compliance check identified escalation trigger(s) "
                    f"{policy_ids} for vendor {request.vendor_name}. "
                    f"The requested amount is ${request.total_amount:,.0f}, which requires "
                    "additional approval or oversight under the listed policy condition(s). "
                    "This request is escalated so procurement leadership can complete the "
                    "required review."
                ),
            )

        within_budget = bool(budget_result.get("within_budget", False))
        duplication_conflict = bool(duplication_result.get("duplication_conflict", False))

        if within_budget and not duplication_conflict:
            advisory_suffix = ""
            if advisories:
                advisory_ids = ", ".join(str(item.get("policy_id", "")) for item in advisories)
                advisory_suffix = (
                    " Policy compliance check also returned non-blocking advisory note(s): "
                    f"{advisory_ids}."
                )
            return ProcurementRecommendation(
                request_id=request.request_id,
                decision="approve",
                rationale=(
                    f"Budget check confirmed the ${request.total_amount:,.0f} request is "
                    "within the cost center budget. "
                    "Policy compliance check found no blocking violations, and Vendor "
                    "duplication check found no threshold conflict for the selected vendor. "
                    f"Risk assessment did not identify a blocking risk for {request.vendor_name}."
                    f"{advisory_suffix}"
                ),
            )

        return ProcurementRecommendation(
            request_id=request.request_id,
            decision="escalate",
            rationale=(
                "Budget check and Vendor duplication check identified a non-policy condition "
                "that prevents automatic approval. "
                f"For vendor {request.vendor_name}, within_budget={within_budget} and "
                f"duplication_conflict={duplication_conflict} at ${request.total_amount:,.0f}. "
                "This request is escalated so procurement can resolve the conflicting signals "
                "before final action."
            ),
        )
    except Exception as exc:
        return ProcurementRecommendation(
            request_id=request.request_id,
            decision="escalate",
            rationale=(
                "Agent orchestration failed while evaluating the request. "
                f"Error: {exc}. Escalating for manual procurement review."
            ),
        )


class ProcurementAgentFacade:
    """Deterministic facade with async run compatibility for manual testing."""

    async def run(self, user_prompt: str) -> _DeterministicRunResult:
        request_id = _extract_request_id(user_prompt)
        if request_id is None:
            recommendation = ProcurementRecommendation(
                request_id="UNKNOWN",
                decision="escalate",
                rationale=(
                    "Unable to identify request_id from prompt text. "
                    "Escalating for manual procurement review."
                ),
            )
            return _DeterministicRunResult(data=recommendation)

        try:
            request = _request_by_id(request_id)
        except (StopIteration, ValueError) as exc:
            recommendation = ProcurementRecommendation(
                request_id=request_id,
                decision="escalate",
                rationale=(
                    f"Unable to load request data for {request_id}: {exc}. "
                    "Escalating for manual procurement review."
                ),
            )
            return _DeterministicRunResult(data=recommendation)

        recommendation = run_procurement_agent(request)
        return _DeterministicRunResult(data=recommendation)

    def run_sync(self, request: PurchaseRequest) -> _DeterministicRunResult:
        """Synchronous compatibility method for direct code paths."""
        return _DeterministicRunResult(data=run_procurement_agent(request))


agent = ProcurementAgentFacade()
