from sqlalchemy.orm import Session
from app.models.cart_detail import CartDetail
from app.schemas.cart_detail import CartDetailCreate

def create_cart_detail(db: Session, cart_detail: CartDetailCreate):
    db_cart_detail = CartDetail(**cart_detail.dict())
    db.add(db_cart_detail)
    db.commit()
    db.refresh(db_cart_detail)
    return db_cart_detail

def get_cart_detail(db: Session, cart_detail_id: int):
    return db.query(CartDetail).filter(CartDetail.maChiTietGioHang == cart_detail_id).first()

def get_cart_details(db: Session, skip: int = 0, limit: int = 100):
    return db.query(CartDetail).offset(skip).limit(limit).all()

def update_cart_detail(db: Session, cart_detail_id: int, updates: dict):
    db_cart_detail = db.query(CartDetail).filter(CartDetail.maChiTietGioHang == cart_detail_id).first()
    if not db_cart_detail:
        return None
    for key, value in updates.items():
        setattr(db_cart_detail, key, value)
    db.commit()
    db.refresh(db_cart_detail)
    return db_cart_detail

def delete_cart_detail(db: Session, cart_detail_id: int):
    db_cart_detail = db.query(CartDetail).filter(CartDetail.maChiTietGioHang == cart_detail_id).first()
    if not db_cart_detail:
        return None
    db.delete(db_cart_detail)
    db.commit()
    return db_cart_detail
