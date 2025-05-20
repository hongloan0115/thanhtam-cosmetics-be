from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class ProductBase(BaseModel):
    tenSanPham: str = Field(..., max_length=100)
    moTa: Optional[str] = Field(None, max_length=255)
    giaBan: int
    soLuongTonKho: int
    trangThai: Optional[bool] = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    tenSanPham: Optional[str] = Field(None, max_length=100)
    moTa: Optional[str] = Field(None, max_length=255)
    giaBan: Optional[int]
    soLuongTonKho: Optional[int]
    trangThai: Optional[bool]

class ProductOut(ProductBase):
    maSanPham: int
    ngayTao: datetime
    ngayCapNhat: datetime

    class Config:
        orm_mode = True
