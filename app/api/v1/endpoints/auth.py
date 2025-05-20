from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.schemas.user import UserRegister, UserLogin
from app.db.database import get_db
from app.models.role import Role
from app.models.user import User
from app.crud.user import get_user_by_email
from app.core.security import hash_password, verify_password, create_access_token
from app.utils.utils import generate_username, generate_verification_code
from app.utils.email import send_verification_email

router = APIRouter()

@router.post("/register")
async def register_user(user: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email đã tồn tại.")

    hashed_pw = hash_password(user.password)
    username = generate_username()
    verification_code = generate_verification_code()

    role = db.query(Role).filter(Role.tenVaiTro == "KHACHHANG").first()
    if not role:
        raise HTTPException(status_code=500, detail="Vai trò KHACHHANG chưa được cấu hình.")

    new_user = User(
        tenNguoiDung=username,
        email=user.email,
        matKhauMaHoa=hashed_pw,
        tokenXacThuc=verification_code  # Sửa lại đúng tên trường
    )
    new_user.vaiTro.append(role)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    await send_verification_email(user.email, verification_code)

    return {"message": "Đăng ký thành công. Vui lòng kiểm tra email để xác thực."}

@router.get("/verify-email")
def verify_email(code: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.tokenXacThuc == code).first()
    if not user:
        raise HTTPException(status_code=404, detail="Mã xác thực không hợp lệ.")
    if user.daXacThucEmail:
        return {"message": "Email đã được xác thực."}
    
    user.daXacThucEmail = True
    db.commit()
    return {"message": "Xác thực email thành công."}

@router.post("/login")
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_email(db, user_in.email)
    if not user or not verify_password(user_in.password, user.matKhauMaHoa):
        raise HTTPException(status_code=400, detail="Sai tên đăng nhập hoặc mật khẩu.")
    is_admin = any(role.tenVaiTro.lower() == "admin" for role in user.vaiTro)
    if not is_admin and not user.daXacThucEmail:
        raise HTTPException(status_code=400, detail="Email chưa được xác thực.")
    roles = [role.tenVaiTro for role in user.vaiTro]
    access_token = create_access_token(data={"sub": user.email, "roles": roles})
    return {"access_token": access_token, "token_type": "bearer"}
