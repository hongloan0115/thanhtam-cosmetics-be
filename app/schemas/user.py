from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

from app.schemas.role import RoleOut
from app.schemas.cart import CartOut

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    tenNguoiDung: Optional[str] = None
    hoTen: Optional[str] = None
    soDienThoai: Optional[str] = None
    email: EmailStr
    password: str = Field(..., min_length=8)
    vaiTro: Optional[List[int]] = None 

class UserUpdate(BaseModel): 
    tenNguoiDung: Optional[str] = None
    hoTen: Optional[str] = None
    soDienThoai: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    vaiTro: Optional[List[int]] = None
    trangThai: Optional[bool] = None

class UserOut(BaseModel):
    maNguoiDung: int
    tenNguoiDung: Optional[str]
    hoTen: Optional[str]
    soDienThoai: Optional[str]
    email: EmailStr
    daXacThucEmail: bool
    trangThai: bool
    vaiTro: List[RoleOut]
    gioHang: List[CartOut] = []

    model_config = {
        "from_attributes": True
    }

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
