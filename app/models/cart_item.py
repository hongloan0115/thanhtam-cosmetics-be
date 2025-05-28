from sqlalchemy import Column, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum

class TrangThaiGioHangEnum(enum.Enum):
    DACHON = "ĐÃ CHỌN"
    DADAT = "ĐÃ ĐẶT"
    BOQUA = "BỎ QUA"

class CartItem(Base):
    __tablename__ = "GIOHANG"

    maGioHang = Column(Integer, primary_key=True, index=True, autoincrement=True)
    maNguoiDung = Column(Integer, ForeignKey("NGUOIDUNG.maNguoiDung"), nullable=False)
    maSanPham = Column(Integer, ForeignKey("SANPHAM.maSanPham"), nullable=False)
    soLuong = Column(Integer, default=1, nullable=False)
    ngayTao = Column(DateTime(timezone=True), server_default=func.now())
    ngayCapNhat = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    trangThai = Column(Enum(TrangThaiGioHangEnum), default=TrangThaiGioHangEnum.DACHON)

    nguoiDung = relationship("User", back_populates="gioHang")
    sanPham = relationship("Product", back_populates="gioHang")
