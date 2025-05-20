from sqlalchemy.orm import Session
from app.models.user import User

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.tenNguoiDung == username).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.maNguoiDung == user_id).first()

def create_user(db: Session, user: User):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, user_id: int, update_data: dict):
    user = db.query(User).filter(User.maNguoiDung == user_id).first()
    if user:
        for key, value in update_data.items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.maNguoiDung == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()
