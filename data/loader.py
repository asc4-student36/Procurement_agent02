"""Utilities for loading mock procurement datasets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _project_root() -> Path:
    """Return the project root path resolved from this module location."""
    return Path(__file__).resolve().parent.parent


def _load_mock_data(filename: str) -> list[Any]:
    """Load and parse a JSON mock data file from the mock_data directory."""
    file_path = _project_root() / "mock_data" / filename
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_budgets() -> list[Any]:
    """Load budget records from mock_data/budgets.json."""
    return _load_mock_data("budgets.json")


def load_vendors() -> list[Any]:
    """Load vendor records from mock_data/vendors.json."""
    return _load_mock_data("vendors.json")


def load_policies() -> list[Any]:
    """Load policy records from mock_data/policies.json."""
    return _load_mock_data("policies.json")


def load_requests() -> list[Any]:
    """Load purchase request records from mock_data/requests.json."""
    return _load_mock_data("requests.json")
