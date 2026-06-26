"""Tests for agent/tool error-path behavior."""

from __future__ import annotations

from unittest.mock import patch

from agent import run_procurement_agent
from data.loader import load_requests
from models import PurchaseRequest


def _request_by_id(request_id: str) -> PurchaseRequest:
    """Load a sample request by ID from mock data."""
    raw_request = next(item for item in load_requests() if item["request_id"] == request_id)
    payload = {
        key: value
        for key, value in raw_request.items()
        if key in PurchaseRequest.model_fields
    }
    return PurchaseRequest.model_validate(payload)


def test_agent_handles_budget_loader_runtime_error_with_recommendation() -> None:
    """Agent should catch tool failures and return a structured escalation."""
    request = _request_by_id("REQ-001")

    with patch("data.loader.load_budgets", side_effect=RuntimeError("budget loader failure")):
        recommendation = run_procurement_agent(request)

    assert recommendation.decision == "escalate"
    assert isinstance(recommendation.rationale, str)
    assert recommendation.rationale.strip() != ""
    assert "failure" in recommendation.rationale.lower() or "error" in recommendation.rationale.lower()


def test_agent_escalates_for_unknown_vendor_id() -> None:
    """Unknown vendor IDs should surface as an escalated, explained recommendation."""
    request = _request_by_id("REQ-001").model_copy(
        update={
            "vendor_id": "V-999",
            "vendor_name": "Unknown Vendor",
        }
    )

    recommendation = run_procurement_agent(request)

    assert recommendation.decision == "escalate"
    assert isinstance(recommendation.rationale, str)
    assert recommendation.rationale.strip() != ""
    assert "unknown vendor" in recommendation.rationale.lower() or "v-999" in recommendation.rationale.lower()
