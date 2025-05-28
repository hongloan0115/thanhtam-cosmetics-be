from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db.database import Base

class OrderDetail(Base):
    __tablename__ = "CHITIETDONHANG"

    maChiTiet = Column(Integer, primary_key=True, index=True, autoincrement=True)
    maDonHang = Column(Integer, ForeignKey("DONHANG.maDonHang"), nullable=False)
    maSanPham = Column(Integer, ForeignKey("SANPHAM.maSanPham"), nullable=False)
    soLuong = Column(Integer, nullable=False)
    donGia = Column(Float, nullable=False)
    tongTien = Column(Float, nullable=False)

    donHang = relationship("Order", back_populates="chiTietDonHang")
    sanPham = relationship("Product", back_populates="chiTietDonHang")
