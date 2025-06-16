from sqlalchemy.orm import Session
from app.models.image import Image

def get_images(db: Session, maSanPham: int = None):
    query = db.query(Image)
    if maSanPham is not None:
        query = query.filter(Image.maSanPham == maSanPham)
    return query.all()

def get_image_by_id(db: Session, image_id: int):
    return db.query(Image).filter(Image.maHinhAnh == image_id).first()

def create_image(db: Session, image: Image):
    db.add(image)
    db.commit()
    db.refresh(image)
    return image

def update_image(db: Session, image_id: int, image_data: dict):
    image = db.query(Image).filter(Image.maHinhAnh == image_id).first()
    if image:
        for key, value in image_data.items():
            setattr(image, key, value)
        db.commit()
        db.refresh(image)
    return image

def delete_image(db: Session, image_id: int):
    image = db.query(Image).filter(Image.maHinhAnh == image_id).first()
    if image:
        db.delete(image)
        db.commit()
    return image
