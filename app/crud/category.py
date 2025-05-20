from sqlalchemy.orm import Session
from app.models.category import Category

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Category).offset(skip).limit(limit).all()

def get_category_by_id(db: Session, category_id: int):
    return db.query(Category).filter(Category.maDanhMuc == category_id).first()

def create_category(db: Session, category: Category):
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

def update_category(db: Session, category_id: int, update_data: dict):
    category = db.query(Category).filter(Category.maDanhMuc == category_id).first()
    if category:
        for key, value in update_data.items():
            setattr(category, key, value)
        db.commit()
        db.refresh(category)
    return category

def delete_category(db: Session, category_id: int):
    category = db.query(Category).filter(Category.maDanhMuc == category_id).first()
    if category:
        db.delete(category)
        db.commit()
    return category
