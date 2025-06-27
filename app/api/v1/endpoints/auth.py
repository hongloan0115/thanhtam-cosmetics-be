from fastapi import APIRouter, HTTPException, Depends, Body, Request
from sqlalchemy.orm import Session, joinedload

from app.schemas.user import UserRegister, UserLogin, UserOut, UserUpdate
from app.db.database import get_db
from app.models.role import Role
from app.models.user import User
from app.crud.user import get_user_by_email
from app.core.security import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    decode_refresh_token, get_current_user
)
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
        return {
            "message": "Email đã được xác thực.",
            "redirect_url": "http://localhost:3000/auth/login"
        }
    
    user.daXacThucEmail = True
    db.commit()
    return {
        "message": "Bạn đã xác thực thành công",
        "redirect_url": "http://localhost:3000/auth/login"
    }

@router.post("/login")
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_email(db, user_in.email)
    if not user:
        raise HTTPException(status_code=400, detail="Người dùng không tồn tại.")
    if user.email != user_in.email:
        raise HTTPException(status_code=400, detail="Sai tên đăng nhập.")
    if not verify_password(user_in.password, user.matKhauMaHoa):
        raise HTTPException(status_code=400, detail="Sai mật khẩu.")
    if user.trangThai is False:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa")
    is_admin = any(role.tenVaiTro.lower() == "admin" for role in user.vaiTro)
    if not is_admin and not user.daXacThucEmail:
        raise HTTPException(status_code=400, detail="Email chưa được xác thực.")
    roles = [role.tenVaiTro for role in user.vaiTro]
    access_token = create_access_token(data={"sub": user.email, "roles": roles})
    refresh_token = create_refresh_token(data={"sub": user.email, "roles": roles})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.get("/profile", response_model=UserOut)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).options(joinedload(User.gioHang), joinedload(User.vaiTro)).filter(User.maNguoiDung == current_user.maNguoiDung).first()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại.")
    return user

@router.put("/profile", response_model=UserOut)
def update_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.maNguoiDung == current_user.maNguoiDung).first()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại.")
    # Cập nhật các trường cho phép
    if user_update.tenNguoiDung is not None:
        user.tenNguoiDung = user_update.tenNguoiDung
    if user_update.hoTen is not None:
        user.hoTen = user_update.hoTen
    if user_update.soDienThoai is not None:
        user.soDienThoai = user_update.soDienThoai
    if user_update.email is not None:
        # Kiểm tra email đã tồn tại chưa
        existing = db.query(User).filter(User.email == user_update.email, User.maNguoiDung != user.maNguoiDung).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email đã tồn tại.")
        user.email = user_update.email
    # if user_update.anhDaiDien is not None:
    #     user.anhDaiDien = user_update.anhDaiDien
    db.commit()
    db.refresh(user)
    return user

@router.post("/change-password")
def change_password(
    old_password: str = Body(...),
    new_password: str = Body(..., min_length=8),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.maNguoiDung == current_user.maNguoiDung).first()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại.")
    if not verify_password(old_password, user.matKhauMaHoa):
        raise HTTPException(status_code=400, detail="Mật khẩu cũ không đúng.")
    user.matKhauMaHoa = hash_password(new_password)
    db.commit()
    return {"message": "Đổi mật khẩu thành công."}

@router.post("/refresh-token")
def refresh_token(request: Request, db: Session = Depends(get_db)):
    body = request.json() if hasattr(request, "json") else {}
    # Lấy refresh token từ body hoặc header
    import asyncio
    async def get_body():
        return await request.json()
    try:
        body = asyncio.run(get_body())
    except Exception:
        body = {}
    refresh_token = body.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Refresh token is required.")
    payload = decode_refresh_token(refresh_token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Refresh token không hợp lệ hoặc đã hết hạn. Vui lòng đăng nhập lại.")
    email = payload.get("sub")
    roles = payload.get("roles", [])
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại.")
    access_token = create_access_token(data={"sub": user.email, "roles": roles})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
