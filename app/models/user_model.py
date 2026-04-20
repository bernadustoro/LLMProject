from pydantic import BaseModel, Field
from typing import Optional

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=5, max_length=100)
    full_name: str = Field(..., min_length=3, max_length=100)
    is_active: bool = True
    
class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    id: int

    class Config:
        from_attributes = True # Untuk kompatibilitas dengan ORM

    