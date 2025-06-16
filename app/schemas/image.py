from pydantic import BaseModel, Field
from typing import Optional

class ImageBase(BaseModel):
    duongDan: str = Field(..., max_length=255)
    maAnhClound: str = Field(..., max_length=255)
    moTa: Optional[str] = Field(None, max_length=255)
    laAnhChinh: Optional[bool] = False
    maSanPham: Optional[int] = None

class ImageCreate(ImageBase):
    pass

class ImageUpdate(BaseModel):
    duongDan: Optional[str] = Field(None, max_length=255)
    maAnhClound: Optional[str] = Field(None, max_length=255)
    moTa: Optional[str] = Field(None, max_length=255)
    laAnhChinh: Optional[bool] = None
    maSanPham: Optional[int] = None

class ImageOut(ImageBase):
    maHinhAnh: int

    model_config = {
        "from_attributes": True
    }