from sqlalchemy import Column, Integer, DateTime, Numeric, String, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum

class TrangThaiDonHangEnum(enum.Enum):
    CHOXACNHAN = "CHỜ XÁC NHẬN"
    DANGGIAO = "ĐANG GIAO"
    HOANTHANH = "HOÀN THÀNH"
    DABIHUY = "ĐÃ BỊ HUỶ"

class TrangThaiThanhToanEnum(enum.Enum):
    CHUATHANHTOAN = "CHƯA THANH TOÁN"
    DATHANHTOAN = "ĐÃ THANH TOÁN"

class Order(Base):
    __tablename__ = "DONHANG"

    maDonHang = Column(Integer, primary_key=True, autoincrement=True, index=True)
    maNguoiDung = Column(Integer, ForeignKey("NGUOIDUNG.maNguoiDung"), nullable=False)
    ngayDat = Column(DateTime(timezone=True), server_default=func.now())
    tongTien = Column(Numeric(15, 2), nullable=False)
    trangThai = Column(String(50), default="CHOXACNHAN")
    trangThaiThanhToan = Column(String(50), default="CHUATHANHTOAN")
    ghiChu = Column(Text, nullable=True)
    diaChiChiTiet = Column(Text, nullable=False)
    tinhThanh = Column(String(100), nullable=False)
    quanHuyen = Column(String(100), nullable=False)
    phuongXa = Column(String(100), nullable=False)
    maPhuongThuc = Column(Integer, ForeignKey("PHUONGTHUCTHANHTOAN.maPhuongThuc"), nullable=False)

    chiTietDonHang = relationship("OrderDetail", back_populates="donHang")
    nguoiDung = relationship("User", back_populates="donHang")
    phuongThucThanhToan = relationship("PaymentMethod", back_populates="donHang")

    