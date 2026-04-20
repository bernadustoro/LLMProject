from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import sql_item_model, item_model

class ItemService:
    def get_item(self, db: Session, item_id: int) -> Optional[sql_item_model.Item]:
        return db.query(sql_item_model.Item).filter(sql_item_model.Item.id == item_id).first()

    def get_items(self, db: Session, skip: int = 0, limit: int = 100) -> List[sql_item_model.Item]:
        return db.query(sql_item_model.Item).offset(skip).limit(limit).all()

    def create_item(self, db: Session, item: item_model.ItemCreate) -> sql_item_model.Item:
        db_item = sql_item_model.Item(**item.model_dump())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

    def update_item(self, db: Session, item_id: int, item: item_model.ItemUpdate) -> Optional[sql_item_model.Item]:
        db_item = self.get_item(db, item_id)
        if db_item:
            for key, value in item.model_dump(exclude_unset=True).items():
                setattr(db_item, key, value)
            db.commit()
            db.refresh(db_item)
        return db_item

    def delete_item(self, db: Session, item_id: int) -> Optional[sql_item_model.Item]:
        db_item = self.get_item(db, item_id)
        if db_item:
            db.delete(db_item)
            db.commit()
        return db_item

item_service = ItemService()
