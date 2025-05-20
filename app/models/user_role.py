from sqlalchemy import Column, Integer, ForeignKey, Table

from app.db.database import Base

VAITRO_NGUOIDUNG = Table(
    "VAITRO_NGUOIDUNG",
    Base.metadata,
    Column("maVaiTro", Integer, ForeignKey("VAITRO.maVaiTro"), primary_key=True),
    Column("maNguoiDung", Integer, ForeignKey("NGUOIDUNG.maNguoiDung"), primary_key=True),
)