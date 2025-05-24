from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class CartDetailBase(BaseModel):
    maGioHang: int = Field(..., description="ID giỏ hàng")
    maSanPham: int = Field(..., description="ID sản phẩm")
    soLuong: int = Field(..., gt=0, description="Số lượng sản phẩm")
    giaTaiThem: float = Field(..., description="Giá tại thời điểm thêm")

class CartDetailCreate(CartDetailBase):
    pass

class CartDetailUpdate(BaseModel):
    soLuong: Optional[int] = Field(None, gt=0)
    giaTaiThem: Optional[float] = None

class CartDetailOut(CartDetailBase):
    maChiTietGioHang: int
    ngayThem: datetime

    model_config = {
        "from_attributes": True
    }
