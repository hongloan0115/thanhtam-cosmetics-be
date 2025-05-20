from pydantic import BaseModel
from typing import Optional

class RoleBase(BaseModel):
    tenVaiTro: str
    moTa: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    tenVaiTro: Optional[str] = None
    moTa: Optional[str] = None

class RoleOut(RoleBase):
    maVaiTro: int

    class Config:
        orm_mode = True
