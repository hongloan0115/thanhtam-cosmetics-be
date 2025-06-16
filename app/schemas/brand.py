from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BrandBase(BaseModel):
    tenThuongHieu: str = Field(..., max_length=100)
    moTa: Optional[str] = Field(None, max_length=255)
    anhLogo: Optional[str] = Field(None, max_length=255)
    quocGiaXuatXu: Optional[str] = Field(None, max_length=100)
    trangThai: Optional[bool] = Field(default=True)

class BrandCreate(BrandBase):
    pass

class BrandUpdate(BaseModel):
    tenThuongHieu: Optional[str] = Field(None, max_length=100)
    moTa: Optional[str] = Field(None, max_length=255)
    anhLogo: Optional[str] = Field(None, max_length=255)
    quocGiaXuatXu: Optional[str] = Field(None, max_length=100)
    trangThai: Optional[bool] = None

class BrandOut(BrandBase):
    maThuongHieu: int
    ngayTao: datetime
    ngayCapNhat: datetime

    class Config:
        orm_mode = True
