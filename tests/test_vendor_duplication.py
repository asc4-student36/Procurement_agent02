"""Tests for vendor duplication checks."""

from tools.vendor_duplication import check_vendor_duplication


def test_check_vendor_duplication_req_008_conflicts_found() -> None:
    """REQ-008 should flag office supplies conflicts above POL-001 threshold."""
    result = check_vendor_duplication(
        vendor_id="V-012",
        category="office_supplies",
        requested_amount=28_500.0,
    )

    assert result["threshold_triggered"] is True
    assert result["duplication_conflict"] is True
    assert set(result["conflicting_active_vendor_ids"]) == {"V-001", "V-003"}
