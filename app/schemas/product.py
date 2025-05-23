from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.image import ImageOut
from fastapi import Form

class ProductBase(BaseModel):
    tenSanPham: str = Field(..., max_length=100)
    moTa: Optional[str] = Field(None, max_length=255)
    giaBan: Optional[int] = None
    soLuongTonKho: Optional[int] = None
    trangThai: Optional[bool] = True
    maDanhMuc: Optional[int] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    tenSanPham: Optional[str] = Field(None, max_length=100)
    moTa: Optional[str] = Field(None, max_length=255)
    giaBan: Optional[int] = None
    soLuongTonKho: Optional[int] = None
    trangThai: Optional[bool] = None
    maDanhMuc: Optional[int] = None

class ProductOut(ProductBase):
    maSanPham: int
    ngayTao: datetime
    ngayCapNhat: datetime
    hinhAnh: List[ImageOut] = []

    class Config:
        orm_mode = True

class ProductCreateForm:
    def __init__(
        self,
        tenSanPham: str = Form(..., max_length=100),
        moTa: Optional[str] = Form(None, max_length=255),
        giaBan: Optional[int] = Form(None),
        soLuongTonKho: Optional[int] = Form(None),
        trangThai: Optional[bool] = Form(True),
        maDanhMuc: Optional[int] = Form(None),
    ):
        self.tenSanPham = tenSanPham
        self.moTa = moTa
        self.giaBan = giaBan
        self.soLuongTonKho = soLuongTonKho
        self.trangThai = trangThai
        self.maDanhMuc = maDanhMuc

