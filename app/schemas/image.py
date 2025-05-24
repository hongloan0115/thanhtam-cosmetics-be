from pydantic import BaseModel, Field
from typing import Optional

class ImageBase(BaseModel):
    duongDanAnh: str = Field(..., max_length=255)
    maAnhClound: str = Field(..., max_length=255)
    moTa: Optional[str] = Field(None, max_length=255)
    laAnhChinh: Optional[int] = 0
    maSanPham: Optional[int] = None

class ImageCreate(ImageBase):
    pass

class ImageUpdate(BaseModel):
    duongDanAnh: Optional[str] = Field(None, max_length=255)
    maAnhClound: Optional[str] = Field(None, max_length=255)
    moTa: Optional[str] = Field(None, max_length=255)
    laAnhChinh: Optional[int] = None
    maSanPham: Optional[int] = None

class ImageOut(ImageBase):
    maHinhAnh: int

    model_config = {
        "from_attributes": True
    }