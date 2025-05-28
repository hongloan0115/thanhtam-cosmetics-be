from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base

class PaymentMethod(Base):
    __tablename__ = "PHUONGTHUCTHANHTOAN"

    maPhuongThuc = Column(Integer, primary_key=True, autoincrement=True, index=True)
    tenPhuongThuc = Column(String(100), nullable=False)
    moTa = Column(Text, nullable=True)
    daKichHoat = Column(Boolean, default=True)

    donHang = relationship("Order", back_populates="phuongThucThanhToan")
