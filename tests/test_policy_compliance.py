"""Tests for policy compliance evaluation."""

from data.loader import load_requests
from models import PurchaseRequest
from tools.policy_compliance import check_policy_compliance


def _request_by_id(request_id: str) -> PurchaseRequest:
    """Load a sample request by ID from the real mock data files."""
    raw_request = next(item for item in load_requests() if item["request_id"] == request_id)
    payload = {
        key: value
        for key, value in raw_request.items()
        if key in PurchaseRequest.model_fields
    }
    return PurchaseRequest.model_validate(payload)


def test_pol_004_catering_prohibition_req_009_denies() -> None:
    """REQ-009 catering request should trigger POL-004 deny."""
    request = _request_by_id("REQ-009").model_copy(update={"total_amount": 3200.0})

    result = check_policy_compliance(request)

    pol_004 = [
        violation
        for violation in result["violations"]
        if violation["policy_id"] == "POL-004"
    ]
    assert len(pol_004) == 1
    assert pol_004[0]["forced_decision"] == "deny"


def test_pol_002_manager_threshold_is_advisory_only() -> None:
    """Manager approval should be reported as advisory, not a blocking violation."""
    request = _request_by_id("REQ-002")

    result = check_policy_compliance(request)

    pol_002 = [
        advisory
        for advisory in result["advisories"]
        if advisory["policy_id"] == "POL-002"
    ]
    assert len(pol_002) == 1

    blocking_pol_002 = [
        violation
        for violation in result["violations"]
        if violation["policy_id"] == "POL-002"
    ]
    assert blocking_pol_002 == []


def test_pol_003_near_threshold_req_014_escalates() -> None:
    """REQ-014 should escalate due to near-threshold director approval logic."""
    request = _request_by_id("REQ-014")

    result = check_policy_compliance(request)

    near_threshold = [
        violation
        for violation in result["violations"]
        if violation["policy_id"] == "POL-003-NEAR"
    ]
    assert len(near_threshold) == 1
    assert near_threshold[0]["forced_decision"] == "escalate"


def test_pol_005_expired_contract_req_007_denies() -> None:
    """REQ-007 with Crestview vendor should trigger POL-005 deny."""
    request = _request_by_id("REQ-007")

    result = check_policy_compliance(request)

    pol_005 = [
        violation
        for violation in result["violations"]
        if violation["policy_id"] == "POL-005"
    ]
    assert len(pol_005) == 1
    assert pol_005[0]["forced_decision"] == "deny"
