from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.order_detail import OrderDetail
from app.schemas.order_detail import OrderDetailCreate, OrderDetailUpdate

def get_order_detail(db: Session, maChiTiet: int) -> Optional[OrderDetail]:
    return db.query(OrderDetail).filter(OrderDetail.maChiTiet == maChiTiet).first()

def get_order_details(db: Session, skip: int = 0, limit: int = 100) -> List[OrderDetail]:
    return db.query(OrderDetail).offset(skip).limit(limit).all()

def create_order_detail(db: Session, obj_in: OrderDetailCreate) -> OrderDetail:
    db_obj = OrderDetail(
        maDonHang=obj_in.maDonHang,
        maSanPham=obj_in.maSanPham,
        soLuong=obj_in.soLuong,
        donGia=obj_in.donGia,
        tongTien=obj_in.tongTien,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_order_detail(db: Session, db_obj: OrderDetail, obj_in: OrderDetailUpdate) -> OrderDetail:
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_order_detail(db: Session, maChiTiet: int) -> Optional[OrderDetail]:
    obj = db.query(OrderDetail).filter(OrderDetail.maChiTiet == maChiTiet).first()
    if obj:
        db.delete(obj)
        db.commit()
    return obj
