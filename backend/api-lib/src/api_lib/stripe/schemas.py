from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from decimal import Decimal


class Product(BaseModel):
    default_price: Optional[str]
    livemode: bool
    metadata: Optional[Dict[Any, Any]]
    object: str
    package_dimensions: Optional[Dict[Any, Any]]
    created: Decimal
    statement_descriptor: Optional[str]
    attributes: List[Any]
    shippable: Optional[bool]
    url: Optional[str]
    name: str
    active: bool
    updated: Decimal
    images: List[str]
    marketing_features: List[Dict[Any, Any]]
    tax_code: Optional[str]
    description: Optional[str]
    id: str
    unit_label: Optional[str]
    type: str


class Price(BaseModel):
    id: str
    object: str
    active: bool
    billing_scheme: str
    created: int
    currency: str
    custom_unit_amount: Optional[Dict[str, Any]]
    livemode: bool
    lookup_key: Optional[str]
    metadata: Optional[Dict[str, Any]]
    nickname: Optional[str]
    product: str
    recurring: Optional[Dict[str, Any]]
    tax_behavior: Optional[str]
    tiers_mode: Optional[str]
    transform_quantity: Optional[Dict[str, Any]]
    type: Optional[str]
    unit_amount: Optional[int]
    unit_amount_decimal: Optional[str]


class RankedProduct(BaseModel):
    id: str
    images: List[str]
    name: str
    quantity: int
