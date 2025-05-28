from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.cart_item import TrangThaiGioHangEnum, CartItem
from app.schemas.cart_item import CartItemOut, CartItemCreate, CartItemUpdate
from pydantic import BaseModel

router = APIRouter()

class CartItemCreateRequest(BaseModel):
    maSanPham: int
    soLuong: int = 1

@router.get("/cart/items", response_model=List[CartItemOut])
def get_cart_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    items = db.query(CartItem).filter(
        CartItem.maNguoiDung == current_user.maNguoiDung,
        CartItem.trangThai == TrangThaiGioHangEnum.DACHON
    ).all()
    return items

@router.post("/cart/items", response_model=CartItemOut)
def add_item_to_cart(
    item: CartItemCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = db.query(CartItem).filter(
        CartItem.maNguoiDung == current_user.maNguoiDung,
        CartItem.maSanPham == item.maSanPham,
        CartItem.trangThai == TrangThaiGioHangEnum.DACHON
    ).first()
    if db_item:
        db_item.soLuong += item.soLuong
        db.commit()
        db.refresh(db_item)
        return db_item
    new_item = CartItem(
        maNguoiDung=current_user.maNguoiDung,
        maSanPham=item.maSanPham,
        soLuong=item.soLuong,
        trangThai=TrangThaiGioHangEnum.DACHON
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.put("/cart/items/{cart_item_id}", response_model=CartItemOut)
def update_cart_item(
    cart_item_id: int,
    update: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart_item = db.query(CartItem).filter(
        CartItem.maGioHang == cart_item_id,
        CartItem.maNguoiDung == current_user.maNguoiDung,
        CartItem.trangThai == TrangThaiGioHangEnum.DACHON
    ).first()
    if not cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found in cart")
    if update.soLuong is not None:
        cart_item.soLuong = update.soLuong
    db.commit()
    db.refresh(cart_item)
    return cart_item

@router.delete("/cart/items/{cart_item_id}", response_model=None)
def remove_cart_item(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart_item = db.query(CartItem).filter(
        CartItem.maGioHang == cart_item_id,
        CartItem.maNguoiDung == current_user.maNguoiDung,
        CartItem.trangThai == TrangThaiGioHangEnum.DACHON
    ).first()
    if not cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found in cart")
    db.delete(cart_item)
    db.commit()
    return {"message": "Item removed from cart"}

@router.delete("/cart/clear", response_model=None)
def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db.query(CartItem).filter(
        CartItem.maNguoiDung == current_user.maNguoiDung,
        CartItem.trangThai == TrangThaiGioHangEnum.DACHON
    ).delete()
    db.commit()
    return {"message": "Cart cleared successfully"}

@router.put("/cart/select", response_model=None)
def select_cart_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    items = db.query(CartItem).filter(
        CartItem.maNguoiDung == current_user.maNguoiDung,
        CartItem.trangThai == TrangThaiGioHangEnum.DACHON
    ).all()
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không có sản phẩm nào để đặt hàng")
    for item in items:
        item.trangThai = TrangThaiGioHangEnum.DADAT
    db.commit()
    return {"message": "Đã đánh dấu các sản phẩm là đã đặt hàng"}
