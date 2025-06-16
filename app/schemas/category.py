from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CategoryBase(BaseModel):
    tenDanhMuc: str = Field(..., max_length=100)
    moTa: Optional[str] = Field(None, max_length=255)
    trangThai: Optional[bool] = Field(default=True)
    daXoa: Optional[bool] = Field(default=False)

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    tenDanhMuc: Optional[str] = Field(None, max_length=100)
    moTa: Optional[str] = Field(None, max_length=255)
    trangThai: Optional[bool] = None
    daXoa: Optional[bool] = None

class CategoryOut(CategoryBase):
    maDanhMuc: int
    ngayTao: datetime
    ngayCapNhat: datetime
    soLuongSanPham: int = Field(..., ge=0)  # soLuongSanPham is required and must be non-negative

    class Config:
        orm_mode = True
