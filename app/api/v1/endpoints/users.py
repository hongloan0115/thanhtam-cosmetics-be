from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_admin
from app.schemas.user import UserOut, UserCreate, UserUpdate
from app.crud import user as crud_user
from app.models.user import User
from app.models.role import Role
from app.core.security import hash_password
from app.utils.utils import generate_username

router = APIRouter()

@router.get("/", response_model=list[UserOut])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    return crud_user.get_users(db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserOut)
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    user = crud_user.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    existing_user = crud_user.get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email đã tồn tại.")
    
    username = user_in.tenNguoiDung or generate_username()
    hashed_pw = hash_password(user_in.password)
    new_user = User(
        tenNguoiDung=username if username else None,
        hoTen=user_in.hoTen if user_in.hoTen else None,
        soDienThoai=user_in.soDienThoai if user_in.soDienThoai else None,
        email=user_in.email,
        matKhauMaHoa=hashed_pw,
        daXacThucEmail=True,
        trangThai=True
    )
    # Gán vai trò nếu có
    if user_in.vaiTro:
        roles = db.query(Role).filter(Role.maVaiTro.in_(user_in.vaiTro)).all()
        new_user.vaiTro = roles
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    update_data = user_in.dict(exclude_unset=True)
    if "password" in update_data:
        from app.core.security import hash_password
        update_data["matKhauMaHoa"] = hash_password(update_data.pop("password"))
    # Xử lý cập nhật vai trò nếu có
    if "vaiTro" in update_data and update_data["vaiTro"] is not None:
        roles = db.query(Role).filter(Role.maVaiTro.in_(update_data["vaiTro"])).all()
        update_data["vaiTro"] = roles
    user = crud_user.update_user(db, user_id, update_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}", response_model=UserOut)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    user = crud_user.delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
