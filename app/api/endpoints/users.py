from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, TypeVar, Generic
from pydantic import BaseModel

from app.db.database import get_db
from app.models import user_model
from app.services.user_service import user_service

router = APIRouter()

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    status: str
    code: int
    body: T
    
    
    
@router.get("/", response_model=APIResponse[List[user_model.UserInDB]])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = user_service.get_users(db, skip=skip, limit=limit)
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found")
    return {
        "status": "success",
        "code": status.HTTP_200_OK,
        "body": users
    }
    
@router.post("/", response_model=APIResponse[user_model.UserInDB], status_code=status.HTTP_201_CREATED)
def create_new_user(user: user_model.UserCreate, db: Session = Depends(get_db)):
    db_user = user_service.create_user(db, user)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User creation failed")
    else:
        return {
            "status": "success",
            "code": status.HTTP_201_CREATED,
            "body": db_user
        }
