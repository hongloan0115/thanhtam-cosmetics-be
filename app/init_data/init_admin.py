from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.core.config import settings
from app.core.security import hash_password

from app.models.user import User
from app.models.role import Role

def init_admin():
    """
    Initialize the admin user if not exists and assign ADMIN role.
    """
    db: Session = SessionLocal()

    admin_user = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
    if not admin_user:
        admin_user = User(
            email=settings.ADMIN_EMAIL,
            matKhauMaHoa=hash_password(settings.ADMIN_PASSWORD)
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        admin_role = db.query(Role).filter(Role.tenVaiTro == "ADMIN").first()
        if admin_role:
            admin_user.vaiTro = [admin_role]
            db.commit()
            db.refresh(admin_user)

    return admin_user
