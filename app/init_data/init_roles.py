from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.role import Role

def init_roles():
    db: Session = SessionLocal()

    roles = ['ADMIN', 'KHACHHANG', 'NHANVIEN']
    for role in roles:
        existing_role = db.query(Role).filter(Role.tenVaiTro == role).first()
        if not existing_role:
            new_role = Role(tenVaiTro=role, moTa=f"Vai trò {role}")
            db.add(new_role)

    db.commit()
    db.close()
