from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.database import Base

class Category(Base):
    __tablename__ = "DANHMUC"

    maDanhMuc = Column(Integer, primary_key=True, index=True)
    tenDanhMuc = Column(String(100), unique=True, index=True)
    moTa = Column(String(255))
    trangThai = Column(Boolean, default=True)
    daXoa = Column(Boolean, default=False)

    ngayTao = Column(DateTime(timezone=True), server_default=func.now())
    ngayCapNhat = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    sanPham = relationship("Product", back_populates="danhMuc", lazy="joined")
