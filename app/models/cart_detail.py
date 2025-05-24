from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric, func
from sqlalchemy.orm import relationship
from app.db.database import Base

class CartDetail(Base):
    __tablename__ = "CHITIETGIOHANG"

    maChiTietGioHang = Column(Integer, primary_key=True, autoincrement=True)
    maGioHang = Column(Integer, ForeignKey("GIOHANG.maGioHang", ondelete="CASCADE"), nullable=False)
    maSanPham = Column(Integer, ForeignKey("SANPHAM.maSanPham"), nullable=False)
    soLuong = Column(Integer, nullable=False, default=1)
    giaTaiThem = Column(Numeric(10, 2), nullable=False)
    ngayThem = Column(DateTime(timezone=True), server_default=func.now())

    sanPham = relationship("Product", back_populates="chiTietGioHang")
    gioHang = relationship("Cart", back_populates="chiTietGioHang")