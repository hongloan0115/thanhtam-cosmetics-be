from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class PaymentByVNPAY(Base):
    __tablename__ = "THANHTOANVNPAY"

    maThanhToan = Column(Integer, primary_key=True, autoincrement=True, index=True)
    maDonHang = Column(Integer, ForeignKey("DONHANG.maDonHang"), nullable=False)
    vnp_TxnRef = Column(String(100), nullable=True)
    vnp_Amount = Column(Numeric(15, 2), nullable=True)
    vnp_OrderInfo = Column(Text, nullable=True)
    vnp_ResponseCode = Column(String(10), nullable=True)
    vnp_TransactionNo = Column(String(100), nullable=True)
    vnp_PayDate = Column(DateTime, nullable=True)
    trangThai = Column(String(50), nullable=True)

    donHang = relationship("Order")
