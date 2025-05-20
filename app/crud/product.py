from sqlalchemy.orm import Session

from app.models.product import Product

def get_products(db: Session):
    return db.query(Product).all()

def get_product_by_id(db: Session, product_id: int):
    return db.query(Product).filter(Product.maSanPham == product_id).first()

def create_product(db: Session, product: Product):
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def update_product(db: Session, product_id: int, product_data: dict):
    product = db.query(Product).filter(Product.maSanPham == product_id).first()
    if product:
        for key, value in product_data.items():
            setattr(product, key, value)
        db.commit()
        db.refresh(product)
    return product

def delete_product(db: Session, product_id: int):
    product = db.query(Product).filter(Product.maSanPham == product_id).first()
    if product:
        db.delete(product)
        db.commit()
    return product
