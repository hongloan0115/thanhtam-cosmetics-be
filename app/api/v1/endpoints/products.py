from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_admin
from app.models.product import Product
from app.crud import product as crud_product
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut

router = APIRouter()

@router.get("/", response_model=list[ProductOut])
def read_products(db: Session = Depends(get_db)):
    products = crud_product.get_products(db)
    return products

@router.get("/{product_id}", response_model=ProductOut)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = crud_product.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin)
):
    product = Product(**product_in.dict())
    return crud_product.create_product(db, product)

@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin)
):
    product_data = product_in.dict(exclude_unset=True)
    product = crud_product.update_product(db, product_id, product_data)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.delete("/{product_id}", response_model=ProductOut)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin)
):
    product = crud_product.delete_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
