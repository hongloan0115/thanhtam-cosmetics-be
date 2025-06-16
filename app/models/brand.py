from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Brand(Base):
    __tablename__ = "THUONGHIEU"

    maThuongHieu = Column(Integer, primary_key=True, index=True)
    tenThuongHieu = Column(String(100), unique=True, index=True, nullable=False)
    moTa = Column(Text, nullable=True)  
    anhLogo = Column(String(255), nullable=True)  
    quocGiaXuatXu = Column(String(100), nullable=True)  
    trangThai = Column(Boolean, default=True)  
    ngayTao = Column(DateTime(timezone=True), server_default=func.now())  
    ngayCapNhat = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())  

    sanPham = relationship("Product", back_populates="thuongHieu")
