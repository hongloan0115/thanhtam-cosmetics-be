from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
import enum

class CartStatusEnum(str, enum.Enum):
    HOATDONG = "HOẠT ĐỘNG"
    DADAT = "ĐÃ ĐẶT"
    BOQUA = "BỎ QUA"

class CartBase(BaseModel):
    maNguoiDung: int = Field(..., description="ID người dùng")
    trangThai: Optional[CartStatusEnum] = CartStatusEnum.HOATDONG

class CartCreate(CartBase):
    pass

class CartUpdate(BaseModel):
    trangThai: Optional[CartStatusEnum] = None

class CartOut(CartBase):
    maGioHang: int
    ngayTao: datetime
    ngayCapNhat: datetime

    model_config = {
        "from_attributes": True
    }
