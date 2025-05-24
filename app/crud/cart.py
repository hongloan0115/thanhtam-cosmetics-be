from sqlalchemy.orm import Session
from app.models.cart import Cart, TrangThaiGioHangEnum
from app.schemas.cart import CartCreate, CartUpdate

def get_cart(db: Session, cart_id: int):
    return db.query(Cart).filter(Cart.maGioHang == cart_id).first()

def get_carts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Cart).offset(skip).limit(limit).all()

def create_cart(db: Session, cart_in: CartCreate):
    db_cart = Cart(
        maNguoiDung=cart_in.maNguoiDung,
        trangThai=cart_in.trangThai or TrangThaiGioHangEnum.HOATDONG
    )
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    return db_cart

def update_cart(db: Session, cart_id: int, cart_in: CartUpdate):
    db_cart = db.query(Cart).filter(Cart.maGioHang == cart_id).first()
    if not db_cart:
        return None
    update_data = cart_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_cart, field, value)
    db.commit()
    db.refresh(db_cart)
    return db_cart

def delete_cart(db: Session, cart_id: int):
    db_cart = db.query(Cart).filter(Cart.maGioHang == cart_id).first()
    if not db_cart:
        return None
    db.delete(db_cart)
    db.commit()
    return db_cart
