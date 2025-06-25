from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.image import ImageOut
from fastapi import Form
from app.models.product import TrangThaiSanPham

class ProductBase(BaseModel):
    tenSanPham: str = Field(..., max_length=100)
    moTa: Optional[str] = Field(None, max_length=255)
    giaBan: Optional[int] = None
    soLuongTonKho: Optional[int] = None
    giamGia: Optional[float] = None
    trangThai: Optional[TrangThaiSanPham] = TrangThaiSanPham.DANGBAN
    maDanhMuc: Optional[int] = None
    maThuongHieu: Optional[int] = None  # Thay thế thuongHieu

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    tenSanPham: Optional[str] = Field(None, max_length=100)
    moTa: Optional[str] = Field(None, max_length=255)
    giaBan: Optional[int] = None
    soLuongTonKho: Optional[int] = None
    giamGia: Optional[float] = None
    trangThai: Optional[TrangThaiSanPham] = None
    maDanhMuc: Optional[int] = None
    maThuongHieu: Optional[int] = None  # Thay thế thuongHieu

class ProductOut(ProductBase):
    maSanPham: int
    ngayTao: datetime
    ngayCapNhat: datetime
    hinhAnh: List[ImageOut] = Field(default_factory=list)

    model_config = {
        "from_attributes": True
    }

class ProductCreateForm:
    def __init__(
        self,
        tenSanPham: str = Form(..., max_length=100),
        moTa: Optional[str] = Form(None, max_length=255),
        giaBan: Optional[int] = Form(None),
        soLuongTonKho: Optional[int] = Form(None),
        giamGia: Optional[float] = Form(None),
        # trangThai: Optional[TrangThaiSanPham] = Form(TrangThaiSanPham.DANGBAN),
        maDanhMuc: Optional[int] = Form(...),
        maThuongHieu: Optional[int] = Form(...),  # Thay thế thuongHieu
    ):
        self.tenSanPham = tenSanPham
        self.moTa = moTa
        self.giaBan = giaBan
        self.soLuongTonKho = soLuongTonKho
        self.giamGia = giamGia
        # self.trangThai = trangThai
        self.maDanhMuc = maDanhMuc
        self.maThuongHieu = maThuongHieu

class ProductUpdateForm:
    def __init__(
        self,
        tenSanPham: Optional[str] = Form(None, max_length=100),
        moTa: Optional[str] = Form(None, max_length=255),
        giaBan: Optional[int] = Form(None),
        soLuongTonKho: Optional[int] = Form(None),
        giamGia: Optional[float] = Form(None),
        # trangThai: Optional[TrangThaiSanPham] = Form(None),
        maDanhMuc: Optional[int] = Form(None),
        maThuongHieu: Optional[int] = Form(None),  # Thay thế thuongHieu
        keep_image_ids: Optional[str] = Form(None),  # Chuỗi id, phân tách bởi dấu phẩy, ví dụ: "1,2,3"
    ):
        self.tenSanPham = tenSanPham
        self.moTa = moTa
        self.giaBan = giaBan
        self.soLuongTonKho = soLuongTonKho
        self.giamGia = giamGia
        # self.trangThai = trangThai
        self.maDanhMuc = maDanhMuc
        self.maThuongHieu = maThuongHieu
        self.keep_image_ids = keep_image_ids

