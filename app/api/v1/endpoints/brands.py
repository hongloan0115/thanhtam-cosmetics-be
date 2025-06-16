from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_admin
from app.schemas.brand import BrandCreate, BrandUpdate, BrandOut
from app.crud import brand as crud_brand

router = APIRouter()

@router.get("/", response_model=list[BrandOut])
def get_brands(
    page: int = 1,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    skip = (page - 1) * limit
    brands = crud_brand.get_brands(db, skip=skip, limit=limit)
    return brands

@router.get("/{brand_id}", response_model=BrandOut)
def get_brand(
    brand_id: int,
    db: Session = Depends(get_db)
):
    brand = crud_brand.get_brand_by_id(db, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Không tìm thấy thương hiệu")
    return brand

@router.post("/", response_model=BrandOut, status_code=status.HTTP_201_CREATED)
def create_brand(
    brand_in: BrandCreate,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin)
):
    existing = crud_brand.get_brand_by_name(db, brand_in.tenThuongHieu)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Thương hiệu đã tồn tại"
        )
    return crud_brand.create_brand(db, brand_in)

@router.put("/{brand_id}", response_model=BrandOut)
def update_brand(
    brand_id: int,
    brand_in: BrandUpdate,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin)
):
    update_data = brand_in.dict(exclude_unset=True)
    if "tenThuongHieu" in update_data:
        existing = crud_brand.get_brand_by_name(db, update_data["tenThuongHieu"])
        if existing and existing.maThuongHieu != brand_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Thương hiệu đã tồn tại"
            )
    brand = crud_brand.update_brand(db, brand_id, update_data)
    if not brand:
        raise HTTPException(status_code=404, detail="Không tìm thấy thương hiệu")
    return brand

@router.delete("/{brand_id}", response_model=BrandOut)
def delete_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin)
):
    brand = crud_brand.delete_brand(db, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Không tìm thấy thương hiệu hoặc còn sản phẩm thuộc thương hiệu này")
    return brand
