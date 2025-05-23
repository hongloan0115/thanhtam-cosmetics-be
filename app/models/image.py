from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Image(Base):
    __tablename__ = "HINHANH"

    maHinhAnh = Column(Integer, primary_key=True, index=True)
    duongDanAnh = Column(String(255), nullable=False)
    maAnhClound = Column(String(255), nullable=False)
    moTa = Column(String(255))
    laAnhChinh = Column(Integer, nullable=False, default=0)
    maSanPham = Column(Integer, ForeignKey("SANPHAM.maSanPham"))

    sanPham = relationship("Product", back_populates="hinhAnh")
