"""Vendor risk assessment tool for procurement review workflows."""

from __future__ import annotations

from data import loader

VALID_RISK_LEVELS = {"low", "medium", "high", "critical"}


def _error_result(vendor_id: str, error_type: str, message: str) -> dict[str, object]:
    """Build a typed error payload for risk tool failures."""
    return {
        "vendor_id": vendor_id,
        "compliance_flag": False,
        "contract_status": "unknown",
        "risk_level": "critical",
        "error": message,
        "error_type": error_type,
    }


def assess_risk(vendor_id: str) -> dict[str, object]:
    """Assess vendor risk signals for a purchase request.

    Args:
        vendor_id: Vendor identifier from the purchase request.

    Returns:
        A structured result containing compliance_flag, contract_status, and
        a computed risk_level. For unknown vendors, returns a structured error
        payload without raising an unhandled exception.
    """
    try:
        vendors = loader.load_vendors()
    except FileNotFoundError as exc:
        return _error_result(
            vendor_id,
            "FileNotFoundError",
            f"Vendor data loading failed: {exc}",
        )
    except KeyError as exc:
        return _error_result(
            vendor_id,
            "KeyError",
            f"Vendor data schema error: missing key {exc}",
        )
    except Exception as exc:
        return _error_result(
            vendor_id,
            "Exception",
            f"Unexpected risk assessment tool error: {exc}",
        )

    vendor = next((item for item in vendors if item.get("vendor_id") == vendor_id), None)
    if vendor is None:
        return {
            "vendor_id": vendor_id,
            "compliance_flag": False,
            "contract_status": "unknown",
            "risk_level": "high",
            "error": f"Unknown vendor_id: {vendor_id}",
            "error_type": "KeyError",
        }

    compliance_flag = bool(vendor.get("compliance_flag", False))
    contract_status = str(vendor.get("contract_status", "none"))

    if compliance_flag:
        risk_level = "critical"
    elif contract_status == "expired":
        risk_level = "high"
    elif contract_status == "none":
        risk_level = "medium"
    else:
        risk_level = "low"

    if risk_level not in VALID_RISK_LEVELS:
        return {
            "vendor_id": vendor_id,
            "compliance_flag": compliance_flag,
            "contract_status": contract_status,
            "risk_level": "critical",
            "error": f"Invalid computed risk level: {risk_level}",
            "error_type": "Exception",
        }

    return {
        "vendor_id": vendor_id,
        "compliance_flag": compliance_flag,
        "contract_status": contract_status,
        "risk_level": risk_level,
    }
