from sqlalchemy import Column, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum

# Không được xóa các import này vì chúng cần thiết cho các mối quan hệ và kiểu dữ liệu
from app.models.cart_detail import CartDetail

class TrangThaiGioHangEnum(enum.Enum):
    HOATDONG = "HOẠT ĐỘNG"
    DADAT = "ĐÃ ĐẶT"
    BOQUA = "BỎ QUA"

class Cart(Base):
    __tablename__ = "GIOHANG"

    maGioHang = Column(Integer, primary_key=True, index=True, autoincrement=True)
    maNguoiDung = Column(Integer, ForeignKey("NGUOIDUNG.maNguoiDung"), nullable=False)
    ngayTao = Column(DateTime(timezone=True), server_default=func.now())
    ngayCapNhat = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    trangThai = Column(Enum(TrangThaiGioHangEnum), default=TrangThaiGioHangEnum.HOATDONG)

    nguoiDung = relationship("User", back_populates="gioHang")
    chiTietGioHang = relationship("CartDetail", back_populates="gioHang", cascade="all, delete-orphan")
