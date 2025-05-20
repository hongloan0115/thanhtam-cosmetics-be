from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

from app.schemas.role import RoleOut

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    maNguoiDung: int
    tenNguoiDung: str
    email: EmailStr
    daXacThucEmail: bool
    vaiTro: List[RoleOut]

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
