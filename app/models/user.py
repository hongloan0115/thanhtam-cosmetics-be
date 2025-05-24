from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.user_role import VAITRO_NGUOIDUNG
from app.db.database import Base

# Không được xóa các import này vì chúng cần thiết cho các mối quan hệ và kiểu dữ liệu
from app.models.cart import Cart

class User(Base):
    __tablename__ = "NGUOIDUNG"

    maNguoiDung = Column(Integer, primary_key=True, index=True)
    tenNguoiDung = Column(String(50), unique=True, index=True)
    hoTen = Column(String(100))
    soDienThoai = Column(String(15))

    email = Column(String(100), unique=True, index=True)
    daXacThucEmail = Column(Boolean, default=False)
    tokenXacThuc = Column(String(50), unique=True, index=True)

    matKhauMaHoa = Column(String(100))
    trangThai = Column(Boolean, default=True)
    ngayTao = Column(DateTime(timezone=True), server_default=func.now())
    ngayCapNhat = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    vaiTro = relationship("Role", secondary=VAITRO_NGUOIDUNG, back_populates="nguoiDung")
    gioHang = relationship("Cart", back_populates="nguoiDung")