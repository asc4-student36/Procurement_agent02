"""Vendor duplication check tool for POL-001 single-source restriction."""

from __future__ import annotations

from data import loader

POL001_THRESHOLD = 25_000.0
POL001_AFFECTED_CATEGORIES = {
    "office_supplies",
    "software_licenses",
    "hardware",
    "facilities",
    "security",
    "fleet_parts",
    "staffing",
}


def _error_result(
    vendor_id: str,
    category: str,
    requested_amount: float,
    error_type: str,
    message: str,
) -> dict[str, object]:
    """Build a typed error payload for vendor duplication failures."""
    return {
        "vendor_id": vendor_id,
        "category": category,
        "requested_amount": float(requested_amount),
        "conflicting_active_vendor_ids": [],
        "threshold_triggered": False,
        "duplication_conflict": False,
        "error": message,
        "error_type": error_type,
    }


def check_vendor_duplication(
    vendor_id: str, category: str, requested_amount: float
) -> dict[str, object]:
    """Check for active contracted vendor conflicts under POL-001.

    This tool identifies active contracted vendors in the requested category and
    flags POL-001 threshold-triggered conflict context for policy evaluation.

    Args:
        vendor_id: Requested vendor identifier.
        category: Requested purchase category.
        requested_amount: Total request amount in USD.

    Returns:
        A structured result including:
        - conflicting_active_vendor_ids: list of active contracted vendor IDs in category
          that differ from the requested vendor.
        - threshold_triggered: True when POL-001 threshold conditions are met.
        - duplication_conflict: True when threshold-triggered and conflicts exist.
        - error: Present only if vendor data could not be loaded.
        - error_type: Present for typed error handling.
    """
    try:
        vendors = loader.load_vendors()
    except FileNotFoundError as exc:
        return _error_result(
            vendor_id,
            category,
            requested_amount,
            "FileNotFoundError",
            f"Vendor data loading failed: {exc}",
        )
    except KeyError as exc:
        return _error_result(
            vendor_id,
            category,
            requested_amount,
            "KeyError",
            f"Vendor data schema error: missing key {exc}",
        )
    except Exception as exc:
        return _error_result(
            vendor_id,
            category,
            requested_amount,
            "Exception",
            f"Unexpected vendor duplication tool error: {exc}",
        )

    requested_vendor = next(
        (item for item in vendors if item.get("vendor_id") == vendor_id),
        None,
    )
    requested_is_contracted = (
        requested_vendor is not None
        and requested_vendor.get("category") == category
        and requested_vendor.get("contract_status") == "active"
    )

    conflicting_active_vendor_ids = [
        str(item["vendor_id"])
        for item in vendors
        if item.get("vendor_id") != vendor_id
        and item.get("category") == category
        and item.get("contract_status") == "active"
    ]

    threshold_triggered = (
        float(requested_amount) > POL001_THRESHOLD
        and category in POL001_AFFECTED_CATEGORIES
        and not requested_is_contracted
    )
    duplication_conflict = threshold_triggered and bool(conflicting_active_vendor_ids)

    return {
        "vendor_id": vendor_id,
        "category": category,
        "requested_amount": float(requested_amount),
        "conflicting_active_vendor_ids": conflicting_active_vendor_ids,
        "threshold_triggered": threshold_triggered,
        "duplication_conflict": duplication_conflict,
    }
