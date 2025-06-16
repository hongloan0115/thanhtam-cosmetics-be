from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.brand import Brand
from app.models.product import Product
from app.schemas.brand import BrandCreate

def get_brands(db: Session, skip: int = 0, limit: int = 100):
    brands = (
        db.query(Brand)
        .filter(Brand.trangThai == True)
        .order_by(Brand.maThuongHieu)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return brands

def get_brand_by_id(db: Session, brand_id: int):
    return db.query(Brand).filter(Brand.maThuongHieu == brand_id, Brand.trangThai == True).first()

def get_brand_by_name(db: Session, tenThuongHieu: str):
    return db.query(Brand).filter(Brand.tenThuongHieu == tenThuongHieu, Brand.trangThai == True).first()

def create_brand(db: Session, brand_in: BrandCreate):
    brand = Brand(**brand_in.dict())
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand

def update_brand(db: Session, brand_id: int, update_data: dict):
    brand = db.query(Brand).filter(Brand.maThuongHieu == brand_id, Brand.trangThai == True).first()
    if brand:
        for key, value in update_data.items():
            setattr(brand, key, value)
        db.commit()
        db.refresh(brand)
    return brand

def delete_brand(db: Session, brand_id: int):
    brand = db.query(Brand).filter(Brand.maThuongHieu == brand_id, Brand.trangThai == True).first()
    if not brand:
        return None
    # Kiểm tra xem còn sản phẩm nào chưa bị xóa thuộc thương hiệu này không
    product_count = db.query(Product).filter(
        Product.maThuongHieu == brand_id,
        Product.daXoa == False
    ).count()
    if product_count > 0:
        # Không cho phép xóa nếu còn sản phẩm
        return None
    brand.trangThai = False
    db.commit()
    db.refresh(brand)
    return brand
