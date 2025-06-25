from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_admin
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut
from app.crud import category as crud_category

router = APIRouter()

@router.get("/", response_model=list[CategoryOut])
def get_categories(
    page: int = 1,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    skip = (page - 1) * limit
    categories = crud_category.get_categories(db, skip=skip, limit=limit)
    # categories là list các tuple (Category, soLuongSanPham)
    return [
        {
            **category.__dict__,
            "soLuongSanPham": soLuongSanPham
        }
        for category, soLuongSanPham in categories
    ]

@router.get("/{category_id}", response_model=CategoryOut)
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    result = crud_category.get_category_by_id(db, category_id)
    if not result:
        raise HTTPException(status_code=404, detail="Không tìm thấy danh mục")
    category, soLuongSanPham = result
    return {
        **category.__dict__,
        "soLuongSanPham": soLuongSanPham
    }

@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin)
):
    # Kiểm tra xem danh mục đã tồn tại hay chưa
    existing = crud_category.get_category_by_name(db, category_in.tenDanhMuc)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Danh mục đã tồn tại"
        )
    category = crud_category.create_category(db, category_in)
    # Trả về category vừa tạo, soLuongSanPham mặc định là 0
    return {
        **category.__dict__,
        "soLuongSanPham": getattr(category, "soLuongSanPham", 0)
    }

@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin)
):
    update_data = category_in.dict(exclude_unset=True)
    # Kiểm tra xem tên danh mục có bị trùng lặp không
    if "tenDanhMuc" in update_data:
        existing = crud_category.get_category_by_name(db, update_data["tenDanhMuc"])
        if existing and existing.maDanhMuc != category_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Danh mục đã tồn tại"
            )
    category = crud_category.update_category(db, category_id, update_data)
    if not category:
        raise HTTPException(status_code=404, detail="Không tìm thấy danh mục")
    # Trả về category vừa cập nhật, giữ lại soLuongSanPham nếu có
    return {
        **category.__dict__,
        "soLuongSanPham": getattr(category, "soLuongSanPham", 0)
    }

@router.delete("/{category_id}", response_model=CategoryOut)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin)
):
    category = crud_category.delete_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Không tìm thấy danh mục hoặc còn sản phẩm thuộc danh mục này")
    return {
        **category.__dict__,
        "soLuongSanPham": 0
    }
