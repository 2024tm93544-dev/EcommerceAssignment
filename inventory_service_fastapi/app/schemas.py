from pydantic import BaseModel
from datetime import datetime

class InventoryBase(BaseModel):
    product_id: int
    warehouse: str
    on_hand: int
    reserved: int

class InventoryResponse(InventoryBase):
    inventory_id: int
    reserved_at: datetime | None
    updated_at: datetime
    class Config:
        orm_mode = True

class OperationRequest(BaseModel):
    product_id: int
    warehouse: str
    quantity: int
