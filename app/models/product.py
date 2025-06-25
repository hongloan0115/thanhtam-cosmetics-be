from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Enum
import enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class TrangThaiSanPham(enum.Enum):
    DANGBAN = "ĐANG BÁN"
    SAPHET = "SẮP HẾT"
    HETHANG = "HẾT HÀNG"
    SAPVE = "SẮP VỀ"

class Product(Base):
    __tablename__ = "SANPHAM"

    maSanPham = Column(Integer, primary_key=True, index=True)
    tenSanPham = Column(String(100), nullable=False, index=True)
    moTa = Column(String(255), nullable=True)
    giaBan = Column(Integer, nullable=True, index=True)  # nullable=True để phù hợp schema
    soLuongTonKho = Column(Integer, nullable=True, default=0)  # nullable=True để phù hợp schema
    giamGia = Column(Float, nullable=True, default=0.0)
    trangThai = Column(Enum(TrangThaiSanPham), default=TrangThaiSanPham.DANGBAN, index=True, nullable=False)
    daXoa = Column(Boolean, default=False, nullable=False)

    ngayTao = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ngayCapNhat = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    maThuongHieu = Column(Integer, ForeignKey("THUONGHIEU.maThuongHieu"), index=True, nullable=False)
    thuongHieu = relationship("Brand", back_populates="sanPham")
    maDanhMuc = Column(Integer, ForeignKey("DANHMUC.maDanhMuc"), nullable=False)
    danhMuc = relationship("Category", back_populates="sanPham")
    hinhAnh = relationship("Image", back_populates="sanPham", cascade="all, delete-orphan")
    gioHang = relationship("CartItem", back_populates="sanPham", cascade="all, delete-orphan")
    chiTietDonHang = relationship("OrderDetail", back_populates="sanPham", cascade="all, delete-orphan")