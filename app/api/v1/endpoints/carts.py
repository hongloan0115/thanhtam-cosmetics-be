from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from typing import List

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.cart import TrangThaiGioHangEnum
from app.models.cart import Cart
from app.models.cart_detail import CartDetail
from app.schemas.cart import CartOut
from app.schemas.cart_detail import CartDetailCreate, CartDetailUpdate, CartDetailOut
from app.crud import cart as crud_cart
from app.crud import cart_detail as crud_cart_detail
from pydantic import BaseModel

router = APIRouter()

class AddItemRequest(BaseModel):
    maSanPham: int
    soLuong: int = 1
    giaTaiThem: float

@router.get("/cart", response_model=CartOut)
def get_current_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = db.query(Cart).filter(
        Cart.maNguoiDung == current_user.maNguoiDung,
        Cart.trangThai == TrangThaiGioHangEnum.HOATDONG
    ).first()
    if not cart:
        # raise JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "Cart not found"})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    return cart

@router.get("/cart/items", response_model=List[CartDetailOut])
def get_cart_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = db.query(Cart).filter(
        Cart.maNguoiDung == current_user.maNguoiDung,
        Cart.trangThai == TrangThaiGioHangEnum.HOATDONG
    ).first()
    if not cart:
        return []
    items = db.query(CartDetail).filter(CartDetail.maGioHang == cart.maGioHang).all()
    return items

@router.post("/add-item", response_model=CartOut)
def add_item_to_cart(
    item: AddItemRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Tìm giỏ hàng HOẠT ĐỘNG của user
    cart_query = db.query(Cart).filter(
        Cart.maNguoiDung == current_user.maNguoiDung,
        Cart.trangThai == TrangThaiGioHangEnum.HOATDONG
    )
    db_cart = cart_query.first()

    # 2. Nếu chưa có thì tạo mới
    if not db_cart:
        db_cart = crud_cart.create_cart(
            db,
            cart_in = type("Tmp", (), {
                "maNguoiDung": current_user.maNguoiDung,
                "trangThai": TrangThaiGioHangEnum.HOATDONG
            })()
        )

    # 3. Kiểm tra sản phẩm đã có trong giỏ chưa
    cart_item = db.query(CartDetail).filter(
        CartDetail.maGioHang == db_cart.maGioHang,
        CartDetail.maSanPham == item.maSanPham
    ).first()

    if cart_item:
        # Nếu đã có thì tăng số lượng và cập nhật giá tại thời điểm thêm
        cart_item.soLuong += item.soLuong
        cart_item.giaTaiThem = item.giaTaiThem
        db.commit()
        db.refresh(cart_item)
    else:
        # Nếu chưa có thì thêm mới
        cart_detail_in = CartDetailCreate(
            maGioHang = db_cart.maGioHang,
            maSanPham = item.maSanPham,
            soLuong = item.soLuong,
            giaTaiThem = item.giaTaiThem
        )
        crud_cart_detail.create_cart_detail(db, cart_detail_in)
    db.refresh(db_cart)
    return db_cart

@router.put("/cart/item/{cart_item_id}", response_model=CartDetailOut)
def update_cart_item(
    cart_item_id: int,
    update: CartDetailUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = db.query(Cart).filter(
        Cart.maNguoiDung == current_user.maNguoiDung,
        Cart.trangThai == TrangThaiGioHangEnum.HOATDONG
    ).first()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    cart_item = db.query(CartDetail).filter(
        CartDetail.maChiTietGioHang == cart_item_id,
        CartDetail.maGioHang == cart.maGioHang
    ).first()
    if not cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found in cart")
    # Cập nhật các trường nếu có
    if update.soLuong is not None:
        cart_item.soLuong = update.soLuong
    if update.giaTaiThem is not None:
        cart_item.giaTaiThem = update.giaTaiThem
    db.commit()
    db.refresh(cart_item)
    return cart_item

@router.delete("/cart/clear", response_model=None)
def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Tìm giỏ hàng HOẠT ĐỘNG của user
    cart = db.query(Cart).filter(
        Cart.maNguoiDung == current_user.maNguoiDung,
        Cart.trangThai == TrangThaiGioHangEnum.HOATDONG
    ).first()
    if not cart:
        return {"message": "Cart cleared successfully"}
    # Xóa toàn bộ chi tiết giỏ hàng
    db.query(CartDetail).filter(CartDetail.maGioHang == cart.maGioHang).delete()
    db.commit()
    return {"message": "Cart cleared successfully"}

@router.delete("/cart/item/{cart_item_id}", response_model=None)
def remove_cart_item(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Tìm giỏ hàng HOẠT ĐỘNG của user
    cart = db.query(Cart).filter(
        Cart.maNguoiDung == current_user.maNguoiDung,
        Cart.trangThai == TrangThaiGioHangEnum.HOATDONG
    ).first()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    # Xóa sản phẩm khỏi chi tiết giỏ hàng nếu thuộc giỏ hàng của user
    deleted = db.query(CartDetail).filter(
        CartDetail.maChiTietGioHang == cart_item_id,
        CartDetail.maGioHang == cart.maGioHang
    ).delete()
    db.commit()
    if deleted:
        return {"message": "Item removed from cart"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found in cart")
