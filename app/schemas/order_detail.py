from pydantic import BaseModel
from typing import Optional
from app.schemas.product import ProductOut

class OrderDetailBase(BaseModel):
    maDonHang: Optional[int] = None
    maSanPham: int
    soLuong: int
    donGia: float
    tongTien: float

class OrderDetailCreate(OrderDetailBase):
    pass

class OrderDetailUpdate(BaseModel):
    soLuong: Optional[int] = None
    donGia: Optional[float] = None
    tongTien: Optional[float] = None

class OrderDetailInDBBase(OrderDetailBase):
    maChiTiet: int

    model_config = {
        "from_attributes": True
    }

class OrderDetail(OrderDetailInDBBase):
    pass

class OrderDetailWithProduct(OrderDetailInDBBase):
    sanPham: ProductOut

    class Config:
        orm_mode = True
