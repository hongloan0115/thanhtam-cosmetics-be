from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.category import Category
from app.models.product import Product
from app.schemas.category import CategoryCreate

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    # Lấy các category đã phân trang
    categories = (
        db.query(Category)
        .filter(Category.daXoa == False)
        .order_by(Category.maDanhMuc)
        .offset(skip)
        .limit(limit)
        .all()
    )
    # Lấy số lượng sản phẩm cho từng category
    category_ids = [c.maDanhMuc for c in categories]
    product_counts = dict(
        db.query(Product.maDanhMuc, func.count(Product.maSanPham))
        .filter(Product.maDanhMuc.in_(category_ids), Product.daXoa == False)
        .group_by(Product.maDanhMuc)
        .all()
    )
    # Trả về list tuple (Category, soLuongSanPham)
    return [
        (category, product_counts.get(category.maDanhMuc, 0))
        for category in categories
    ]

def get_category_by_id(db: Session, category_id: int):
    category = db.query(Category).filter(Category.maDanhMuc == category_id, Category.daXoa == False).first()
    if not category:
        return None
    so_luong = db.query(func.count(Product.maSanPham)).filter(Product.maDanhMuc == category_id, Product.daXoa == False).scalar()
    return (category, so_luong or 0)

def get_category_by_name(db: Session, tenDanhMuc: str):
    return db.query(Category).filter(Category.tenDanhMuc == tenDanhMuc, Category.daXoa == False).first()

def create_category(db: Session, category_in: CategoryCreate):
    category = Category(**category_in.dict())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

def update_category(db: Session, category_id: int, update_data: dict):
    category = db.query(Category).filter(Category.maDanhMuc == category_id, Category.daXoa == False).first()
    if category:
        for key, value in update_data.items():
            setattr(category, key, value)
        db.commit()
        db.refresh(category)
    return category

def delete_category(db: Session, category_id: int):
    category = db.query(Category).filter(Category.maDanhMuc == category_id, Category.daXoa == False).first()
    if not category:
        return None
    # Kiểm tra xem còn sản phẩm nào chưa bị xóa thuộc danh mục này không
    product_count = db.query(Product).filter(
        Product.maDanhMuc == category_id,
        Product.daXoa == False
    ).count()
    if product_count > 0:
        # Không cho phép xóa nếu còn sản phẩm
        return None
    category.daXoa = True
    db.commit()
    db.refresh(category)
    return category
