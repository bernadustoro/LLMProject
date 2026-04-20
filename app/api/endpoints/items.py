from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, TypeVar, Generic
from pydantic import BaseModel

from app.db.database import get_db
from app.models import item_model, sql_item_model
from app.services.item_service import item_service
router = APIRouter()

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    status: str
    code: int
    body: T

@router.post("/", response_model=APIResponse[item_model.ItemInDB], status_code=status.HTTP_201_CREATED)
def create_new_item(item: item_model.ItemCreate, db: Session = Depends(get_db)):
    db_item = item_service.create_item(db, item)
    return {
        "status": "success",
        "code": status.HTTP_201_CREATED,
        "body": db_item
    }

@router.get("/", response_model=APIResponse[List[item_model.ItemInDB]])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = item_service.get_items(db, skip=skip, limit=limit)
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No items found")
    return {
        "status": "success",
        "code": status.HTTP_200_OK,
        "body": items
    }

@router.get("/{item_id}", response_model=APIResponse[item_model.ItemInDB])
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = item_service.get_item(db, item_id)
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return {
        "status": "success",
        "code": status.HTTP_200_OK,
        "body": db_item
    }

@router.put("/{item_id}", response_model=APIResponse[item_model.ItemInDB])
def update_existing_item(item_id: int, item: item_model.ItemUpdate, db: Session = Depends(get_db)):
    updated_item = item_service.update_item(db, item_id, item)
    if updated_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return {
        "status": "success",
        "code": status.HTTP_200_OK,
        "body": updated_item
    }

@router.delete("/{item_id}", response_model=APIResponse[dict])
def delete_existing_item(item_id: int, db: Session = Depends(get_db)):
    deleted_item = item_service.delete_item(db, item_id)
    if deleted_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return {
        "status": "success",
        "code": status.HTTP_200_OK,
        "body": {"message": "Item deleted successfully"}
    }
