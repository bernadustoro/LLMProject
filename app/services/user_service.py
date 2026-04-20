from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional
from app.models import sql_user_model, user_model

class UserService:
    def get_users(self, db: Session, skip: int = 0, limit: int = 10) -> List[sql_user_model.User]:
        return db.query(sql_user_model.User).offset(skip).limit(limit).all()
    
    def get_user(self, db: Session, user_id: int) -> Optional[sql_user_model.User]:
        return db.query(sql_user_model.User).filter(sql_user_model.User.id == user_id).first()
    
    def create_user(self, db: Session, user: user_model.UserCreate) -> sql_user_model.User:
        db_user = sql_user_model.User(**user.model_dump())
        db.add(db_user)
        try:
            db.commit()
            db.refresh(db_user)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                code=status.HTTP_400_BAD_REQUEST,
                status = "error",
                detail="data sudah digunakan user lain"
            )
        return db_user

user_service = UserService()