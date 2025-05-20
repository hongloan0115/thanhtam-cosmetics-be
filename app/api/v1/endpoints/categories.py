from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_admin
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut
from app.crud import category as crud_category
from app.models.category import Category

router = APIRouter()

@router.get("/", response_model=list[CategoryOut])
def get_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud_category.get_categories(db, skip=skip, limit=limit)

@router.get("/{category_id}", response_model=CategoryOut)
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    category = crud_category.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin)
):
    category = Category(**category_in.dict())
    return crud_category.create_category(db, category)

@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin)
):
    update_data = category_in.dict(exclude_unset=True)
    category = crud_category.update_category(db, category_id, update_data)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.delete("/{category_id}", response_model=CategoryOut)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin)
):
    category = crud_category.delete_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category
