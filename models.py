from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PurchaseRequest(BaseModel):
    """Typed input model for a procurement purchase request."""

    model_config = ConfigDict(str_strip_whitespace=True)

    request_id: str = Field(min_length=1)
    requestor: str = Field(min_length=1)
    cost_center_id: str = Field(min_length=1)
    vendor_name: str = Field(min_length=1)
    vendor_id: str = Field(min_length=1)
    category: str = Field(min_length=1)
    item_description: str = Field(min_length=1)
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    total_amount: float = Field(gt=0)


class ProcurementRecommendation(BaseModel):
    """Typed output model for the agent's procurement recommendation."""

    model_config = ConfigDict(str_strip_whitespace=True)

    request_id: str = Field(min_length=1)
    decision: Literal["approve", "deny", "escalate"]
    rationale: str = Field(min_length=1)

    @field_validator("rationale")
    @classmethod
    def validate_rationale(cls, value: str) -> str:
        """Reject empty or whitespace-only rationale values."""
        if not value.strip():
            raise ValueError("rationale must be non-empty")
        return value
