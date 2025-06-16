from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Image(Base):
    __tablename__ = "HINHANH"

    maHinhAnh = Column(Integer, primary_key=True, index=True)
    duongDan = Column(String(255), nullable=False)
    maAnhClound = Column(String(255), nullable=False)
    moTa = Column(String(255))
    laAnhChinh = Column(Boolean, nullable=False, default=False)
    daXoa = Column(Boolean, default=False)

    ngayTao = Column(DateTime(timezone=True), server_default=func.now())
    ngayCapNhat = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    maSanPham = Column(Integer, ForeignKey("SANPHAM.maSanPham"))
    sanPham = relationship("Product", back_populates="hinhAnh", lazy="joined")
