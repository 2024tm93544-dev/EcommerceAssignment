from pydantic import BaseModel, Field
from typing import Optional

class ProductBase(BaseModel):
    sku: str = Field(..., max_length=64)
    name: str
    category: Optional[str] = None
    price: float
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str]
    category: Optional[str]
    price: Optional[float]
    is_active: Optional[bool]

class ProductOut(ProductBase):
    product_id: int

class PaginatedProducts(BaseModel):
    items: list[ProductOut]
    page: int
    per_page: int
    total: int
