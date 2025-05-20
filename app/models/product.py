from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Product(Base):
    __tablename__ = "SANPHAM"

    maSanPham = Column(Integer, primary_key=True, index=True)
    tenSanPham = Column(String(100), unique=True, index=True)
    moTa = Column(String(255))
    giaBan = Column(Integer)
    soLuongTonKho = Column(Integer)
    trangThai = Column(Boolean, default=True)
    ngayTao = Column(DateTime(timezone=True), server_default=func.now())
    ngayCapNhat = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    maDanhMuc = Column(Integer, ForeignKey("DANHMUC.maDanhMuc"))
    danhMuc = relationship("Category", back_populates="sanPham")