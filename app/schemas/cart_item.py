from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.product import ProductOut

class CartItemBase(BaseModel):
    maNguoiDung: int = Field(..., description="ID người dùng")
    maSanPham: int = Field(..., description="ID sản phẩm")
    soLuong: int = Field(..., description="Số lượng sản phẩm")

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    soLuong: Optional[int] = None

class CartItemOut(CartItemBase):
    maGioHang: int
    sanPham: Optional[ProductOut] = None

    model_config = {
        "from_attributes": True
    }
