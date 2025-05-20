from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CategoryBase(BaseModel):
    tenDanhMuc: str = Field(..., max_length=100)
    moTa: Optional[str] = Field(None, max_length=255)
    trangThai: Optional[bool] = True

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    tenDanhMuc: Optional[str] = Field(None, max_length=100)
    moTa: Optional[str] = Field(None, max_length=255)
    trangThai: Optional[bool] = None

class CategoryOut(CategoryBase):
    maDanhMuc: int
    ngayTao: datetime
    ngayCapNhat: datetime

    class Config:
        orm_mode = True
