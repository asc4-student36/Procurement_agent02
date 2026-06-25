"""Agent-level tests for procurement recommendation outcomes."""

from __future__ import annotations

import pytest

from agent import agent, run_procurement_agent
from data.loader import load_requests
from models import PurchaseRequest


def _request_by_id(request_id: str) -> PurchaseRequest:
    """Load a sample request by ID from the real mock data files."""
    raw_request = next(item for item in load_requests() if item["request_id"] == request_id)
    payload = {
        key: value
        for key, value in raw_request.items()
        if key in PurchaseRequest.model_fields
    }
    return PurchaseRequest.model_validate(payload)


async def _run_request(request_id: str):
    """Run the async agent for a request loaded from mock_data/requests.json."""
    request = _request_by_id(request_id)
    return await agent.run(str(request))


def _assert_non_empty_rationale(rationale: str) -> None:
    """Assert the rationale string is present and meaningful."""
    assert isinstance(rationale, str)
    assert rationale.strip() != ""


@pytest.mark.asyncio
async def test_agent_req_001_approve() -> None:
    """REQ-001 should approve."""
    result = await _run_request("REQ-001")
    assert result.data.decision == "approve"
    _assert_non_empty_rationale(result.data.rationale)


@pytest.mark.asyncio
async def test_agent_req_006_budget_overage_denies() -> None:
    """REQ-006 should deny due to budget overage on CC-003."""
    result = await _run_request("REQ-006")
    assert result.data.decision == "deny"
    _assert_non_empty_rationale(result.data.rationale)


@pytest.mark.asyncio
async def test_agent_req_009_policy_deny() -> None:
    """REQ-009 should deny due to catering prohibition POL-004."""
    result = await _run_request("REQ-009")
    assert result.data.decision == "deny"
    _assert_non_empty_rationale(result.data.rationale)


@pytest.mark.asyncio
async def test_agent_req_011_escalate() -> None:
    """REQ-011 should escalate due to compliance-flagged vendor."""
    result = await _run_request("REQ-011")
    assert result.data.decision == "escalate"
    _assert_non_empty_rationale(result.data.rationale)


def test_agent_escalates_when_budget_data_file_missing(monkeypatch) -> None:
    """Agent should escalate and mention data loading failure on budget loader errors."""
    from data import loader

    def _raise_file_not_found() -> list[dict[str, object]]:
        raise FileNotFoundError("mock_data/budgets.json not found")

    monkeypatch.setattr(loader, "load_budgets", _raise_file_not_found)

    request = _request_by_id("REQ-001")
    recommendation = run_procurement_agent(request)

    assert recommendation.decision == "escalate"
    assert "loading failed" in recommendation.rationale.lower()
    assert "filenotfounderror" in recommendation.rationale.lower()
