from typing import Optional, List
from pydantic import BaseModel, condecimal
from datetime import datetime
import enum
from app.schemas.user import UserOut, UserOutForOrder
from app.schemas.payment_method import PaymentMethod

from app.schemas.order_detail import OrderDetail, OrderDetailWithProduct

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
    hoTenNguoiNhan: str  # Thêm trường họ tên người nhận
    soDienThoaiNguoiNhan: str  # Thêm trường số điện thoại người nhận

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
    hoTenNguoiNhan: Optional[str] = None  # Thêm trường này
    soDienThoaiNguoiNhan: Optional[str] = None  # Thêm trường này

class OrderOut(OrderBase):
    maDonHang: int
    ngayDat: datetime
    trangThaiThanhToan: Optional[TrangThaiThanhToanEnum]
    chiTietDonHang: Optional[List[OrderDetailWithProduct]] = None  # Thêm dòng này

class OrderOutForAdmin(OrderBase):
    maDonHang: int
    nguoiDung: UserOutForOrder
    ngayDat: datetime
    phuongThucThanhToan: PaymentMethod
    trangThaiThanhToan: Optional[TrangThaiThanhToanEnum]
    chiTietDonHang: Optional[List[OrderDetailWithProduct]] = None

class OrderStatusUpdate(BaseModel):
    trangThai: OrderStatusEnum

class OrderInDBBase(OrderBase):
    maDonHang: int
    ngayDat: datetime
    chiTietDonHang: Optional[List[OrderDetailWithProduct]] = None

    model_config = {
        "from_attributes": True
    }

class Order(OrderInDBBase):
    pass

class OrderCustomerResponse(BaseModel):
    maDonHang: int
    ngayDat: datetime
    trangThai: OrderStatusEnum
    trangThaiThanhToan: Optional[TrangThaiThanhToanEnum]
    phuongThucThanhToan: PaymentMethod
    tongTien: float
    diaChiChiTiet: str
    tinhThanh: str
    quanHuyen: str
    phuongXa: str
    hoTenNguoiNhan: str  # Thêm trường này
    soDienThoaiNguoiNhan: str  # Thêm trường này
    ghiChu: Optional[str] = None
    chiTietDonHang: List[OrderDetailWithProduct]
    payment_url: Optional[str] = None

    class Config:
        orm_mode = True


