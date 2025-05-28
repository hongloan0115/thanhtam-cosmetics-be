from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.models.order import Order
from app.models.order_detail import OrderDetail
from app.schemas.order import OrderCreate, OrderUpdate

def get_order(db: Session, maDonHang: int) -> Optional[Order]:
    return db.query(Order).options(joinedload(Order.chiTietDonHang)).filter(Order.maDonHang == maDonHang).first()

def get_orders(db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
    return db.query(Order).options(joinedload(Order.chiTietDonHang)).offset(skip).limit(limit).all()

def create_order(db: Session, obj_in: OrderCreate) -> Order:
    db_obj = Order(
        maNguoiDung=obj_in.maNguoiDung,
        tongTien=obj_in.tongTien,
        trangThai=obj_in.trangThai.value if obj_in.trangThai else None,
        ghiChu=obj_in.ghiChu,
        diaChiChiTiet=obj_in.diaChiChiTiet,
        tinhThanh=obj_in.tinhThanh,
        quanHuyen=obj_in.quanHuyen,
        phuongXa=obj_in.phuongXa,
        maPhuongThuc=obj_in.maPhuongThuc,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_order(db: Session, db_obj: Order, obj_in: OrderUpdate) -> Order:
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "trangThai" and value is not None:
            setattr(db_obj, field, value.value)
        else:
            setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_order(db: Session, maDonHang: int) -> Optional[Order]:
    obj = db.query(Order).filter(Order.maDonHang == maDonHang).first()
    if obj:
        db.delete(obj)
        db.commit()
    return obj
