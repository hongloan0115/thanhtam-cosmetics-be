from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base

class Role(Base):
    __tablename__ = "VAITRO"

    maVaiTro = Column(Integer, primary_key=True, index=True)
    tenVaiTro = Column(String(50), unique=True, index=True)
    moTa = Column(String(255))
    
    nguoiDung = relationship("User", secondary="VAITRO_NGUOIDUNG", back_populates="vaiTro")