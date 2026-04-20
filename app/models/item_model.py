from pydantic import BaseModel, Field
from typing import Optional

class ItemBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = None
    price: int = Field(..., gt=0)
    is_offer: bool = False

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    name: Optional[str] = None
    price: Optional[int] = None
    description: Optional[str] = None
    is_offer: Optional[bool] = None


class ItemInDB(ItemBase):
    id: int

    class Config:
        from_attributes = True # Untuk kompatibilitas dengan ORM
