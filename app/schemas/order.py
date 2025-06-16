from typing import Optional, List
from pydantic import BaseModel, condecimal
from datetime import datetime
import enum
from app.schemas.user import UserOut, UserOutForOrder
from app.schemas.payment_method import PaymentMethod

from app.schemas.order_detail import OrderDetail

class OrderStatusEnum(str, enum.Enum):
    CHOXACNHAN = "CHỜ XÁC NHẬN"
    DANGGIAO = "ĐANG GIAO"
    HOANTHANH = "HOÀN THÀNH"
    DABIHUY = "ĐÃ BỊ HUỶ"

class TrangThaiThanhToanEnum(enum.Enum):
    CHUATHANHTOAN = "CHƯA THANH TOÁN"
    DATHANHTOAN = "ĐÃ THANH TOÁN"

class OrderBase(BaseModel):
    maNguoiDung: int
    diaChiChiTiet: str
    tinhThanh: str
    quanHuyen: str
    phuongXa: str
    maPhuongThuc: int
    ghiChu: Optional[str] = None
    tongTien: condecimal(max_digits=15, decimal_places=2)
    trangThai: Optional[OrderStatusEnum] = OrderStatusEnum.CHOXACNHAN

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    trangThai: Optional[OrderStatusEnum] = None
    ghiChu: Optional[str] = None
    diaChiChiTiet: Optional[str] = None
    tinhThanh: Optional[str] = None
    quanHuyen: Optional[str] = None
    phuongXa: Optional[str] = None
    maPhuongThuc: Optional[int] = None

class OrderOut(OrderBase):
    maDonHang: int
    ngayDat: datetime
    trangThaiThanhToan: Optional[TrangThaiThanhToanEnum]

class OrderOutForAdmin(OrderBase):
    maDonHang: int
    nguoiDung: UserOutForOrder
    ngayDat: datetime
    phuongThucThanhToan: PaymentMethod
    trangThaiThanhToan: Optional[TrangThaiThanhToanEnum]

class OrderStatusUpdate(BaseModel):
    trangThai: OrderStatusEnum

class OrderInDBBase(OrderBase):
    maDonHang: int
    ngayDat: datetime
    chiTietDonHang: Optional[List[OrderDetail]] = None

    model_config = {
        "from_attributes": True
    }

class Order(OrderInDBBase):
    pass

class OrderCheckoutResponse(BaseModel):
    maDonHang: int
    chiTietDonHang: Optional[List[OrderDetail]] = None
    payment_url: Optional[str] = None


