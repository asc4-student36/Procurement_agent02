"""Budget evaluation tool for procurement requests."""

from __future__ import annotations

from data import loader


def _error_result(
    cost_center_id: str,
    requested_amount: float,
    error_type: str,
    message: str,
) -> dict[str, object]:
    """Build a typed error payload for budget tool failures."""
    return {
        "within_budget": False,
        "remaining_budget": 0.0,
        "overage": float(requested_amount),
        "error": message,
        "error_type": error_type,
        "cost_center_id": cost_center_id,
    }


def check_budget(cost_center_id: str, requested_amount: float) -> dict[str, object]:
    """Check whether a request amount fits within a cost center's remaining budget.

    Args:
        cost_center_id: Cost center identifier to evaluate.
        requested_amount: Total amount requested for purchase.

    Returns:
        A structured result containing:
        - within_budget: True when requested_amount is within remaining budget.
        - remaining_budget: Remaining budget for the matched cost center.
        - overage: Amount above remaining budget, or 0.0 when within budget.
        - error: Present only when the cost center is not found.
        - error_type: Present for typed error handling.
    """
    try:
        budgets = loader.load_budgets()
    except FileNotFoundError as exc:
        return _error_result(
            cost_center_id,
            requested_amount,
            "FileNotFoundError",
            f"Budget data loading failed: {exc}",
        )
    except KeyError as exc:
        return _error_result(
            cost_center_id,
            requested_amount,
            "KeyError",
            f"Budget data schema error: missing key {exc}",
        )
    except Exception as exc:
        return _error_result(
            cost_center_id,
            requested_amount,
            "Exception",
            f"Unexpected budget tool error: {exc}",
        )

    matched_center = next(
        (item for item in budgets if item.get("cost_center_id") == cost_center_id),
        None,
    )

    if matched_center is None:
        return _error_result(
            cost_center_id,
            requested_amount,
            "KeyError",
            f"Unknown cost center: {cost_center_id}",
        )

    remaining_budget = float(matched_center["remaining"])
    requested = float(requested_amount)
    overage = max(0.0, requested - remaining_budget)

    return {
        "within_budget": overage == 0.0,
        "remaining_budget": remaining_budget,
        "overage": overage,
    }
