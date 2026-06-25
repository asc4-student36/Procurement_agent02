"""Policy compliance tool for evaluating purchase requests against all policies."""

from __future__ import annotations

from data import loader
from models import PurchaseRequest

NEAR_DIRECTOR_THRESHOLD_RATIO = 0.95


def _error_result(error_type: str, message: str) -> dict[str, object]:
    """Build a typed error payload for policy tool failures."""
    return {
        "compliant": False,
        "violations": [
            {
                "policy_id": "POL-DATA",
                "rule_description": message,
                "forced_decision": "escalate",
            }
        ],
        "advisories": [],
        "error": message,
        "error_type": error_type,
    }


def check_policy_compliance(request: PurchaseRequest) -> dict[str, object]:
    """Evaluate a purchase request against all configured procurement policies.

    Args:
        request: The purchase request to evaluate.

    Returns:
        A structured result with:
        - compliant: True when no policy violations are found.
        - violations: A list of policy findings with policy_id, rule_description,
          and forced_decision (deny or escalate).
        - advisories: A list of non-blocking policy notes.
        - error: Present only when policy data evaluation fails.
        - error_type: Present for typed error handling.
    """
    try:
        policies = loader.load_policies()
        vendors = loader.load_vendors()
        budgets = loader.load_budgets()
    except FileNotFoundError as exc:
        return _error_result("FileNotFoundError", f"Policy data loading failed: {exc}")
    except KeyError as exc:
        return _error_result("KeyError", f"Policy data schema error: missing key {exc}")
    except Exception as exc:
        return _error_result("Exception", f"Unexpected policy compliance tool error: {exc}")

    vendor = next((item for item in vendors if item.get("vendor_id") == request.vendor_id), None)
    budget = next(
        (item for item in budgets if item.get("cost_center_id") == request.cost_center_id),
        None,
    )
    violations: list[dict[str, str]] = []
    advisories: list[dict[str, str]] = []

    for policy in policies:
        policy_id = str(policy.get("policy_id", ""))
        description = str(policy.get("description", ""))

        if policy_id == "POL-001":
            threshold = float(policy.get("threshold_amount", 25000.0))
            affected_categories = set(policy.get("affected_categories", []))
            requested_vendor_is_active_in_category = (
                vendor is not None
                and vendor.get("category") == request.category
                and vendor.get("contract_status") == "active"
            )
            other_active_vendors = [
                item.get("vendor_id")
                for item in vendors
                if item.get("vendor_id") != request.vendor_id
                and item.get("category") == request.category
                and item.get("contract_status") == "active"
            ]
            if (
                request.total_amount > threshold
                and request.category in affected_categories
                and not requested_vendor_is_active_in_category
                and len(other_active_vendors) > 0
            ):
                violations.append(
                    {
                        "policy_id": policy_id,
                        "rule_description": description,
                        "forced_decision": "deny",
                    }
                )

        elif policy_id == "POL-002":
            threshold = float(policy.get("threshold_amount", 10000.0))
            upper_threshold = float(policy.get("upper_threshold", 49999.99))
            if threshold <= request.total_amount <= upper_threshold:
                advisories.append(
                    {
                        "policy_id": policy_id,
                        "note": (
                            "Manager approval is required before processing this request."
                        ),
                    }
                )

        elif policy_id == "POL-003":
            threshold = float(policy.get("threshold_amount", 50000.0))
            if request.total_amount >= threshold:
                violations.append(
                    {
                        "policy_id": policy_id,
                        "rule_description": description,
                        "forced_decision": "escalate",
                    }
                )
            elif request.total_amount >= threshold * NEAR_DIRECTOR_THRESHOLD_RATIO:
                violations.append(
                    {
                        "policy_id": "POL-003-NEAR",
                        "rule_description": (
                            "Purchase amount is within 5% of the director approval "
                            "threshold and requires escalation for director awareness."
                        ),
                        "forced_decision": "escalate",
                    }
                )

        elif policy_id == "POL-004":
            affected_categories = set(policy.get("affected_categories", []))
            if request.category in affected_categories:
                violations.append(
                    {
                        "policy_id": policy_id,
                        "rule_description": description,
                        "forced_decision": "deny",
                    }
                )

        elif policy_id == "POL-005":
            if vendor is not None and vendor.get("contract_status") == "expired":
                violations.append(
                    {
                        "policy_id": policy_id,
                        "rule_description": description,
                        "forced_decision": "deny",
                    }
                )

        elif policy_id == "POL-006":
            if vendor is not None and vendor.get("compliance_flag") is True:
                violations.append(
                    {
                        "policy_id": policy_id,
                        "rule_description": description,
                        "forced_decision": "escalate",
                    }
                )

        elif policy_id == "POL-007":
            if request.category == "staffing":
                vendor_is_active_staffing_contract = (
                    vendor is not None
                    and vendor.get("category") == "staffing"
                    and vendor.get("contract_status") == "active"
                )
                if request.quantity > 40 and not vendor_is_active_staffing_contract:
                    violations.append(
                        {
                            "policy_id": policy_id,
                            "rule_description": description,
                            "forced_decision": "deny",
                        }
                    )

        elif policy_id == "POL-008":
            if budget is not None and request.total_amount > float(budget.get("remaining", 0.0)):
                violations.append(
                    {
                        "policy_id": policy_id,
                        "rule_description": description,
                        "forced_decision": "deny",
                    }
                )

    return {
        "compliant": len(violations) == 0,
        "violations": violations,
        "advisories": advisories,
    }
