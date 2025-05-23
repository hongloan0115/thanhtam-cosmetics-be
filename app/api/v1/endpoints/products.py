from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.core.security import get_current_admin
from app.models.product import Product
from app.models.image import Image
from app.crud import product as crud_product
from app.schemas.product import ProductUpdate, ProductOut, ProductCreateForm
from app.schemas.image import ImageOut
import cloudinary
import cloudinary.uploader
import filetype
from app.core.config import settings

router = APIRouter()

# Thiết lập Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUD_NAME,
    api_key=settings.API_KEY,
    api_secret=settings.API_SECRET
)

@router.get("/", response_model=list[ProductOut])
def read_products(db: Session = Depends(get_db)):
    products = crud_product.get_products(db)
    result = []
    for product in products:
        main_images = [img for img in product.hinhAnh if img.laAnhChinh == 1]
        product_out = ProductOut.from_orm(product)
        product_out.hinhAnh = [ImageOut.from_orm(main_images[0])] if main_images else []
        result.append(product_out)
    return result

@router.get("/{product_id}", response_model=ProductOut)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = crud_product.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    main_images = [img for img in product.hinhAnh if img.laAnhChinh == 1]
    product_out = ProductOut.from_orm(product)
    product_out.hinhAnh = [ImageOut.from_orm(main_images[0])] if main_images else []
    return product_out

@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreateForm = Depends(),
    images: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin)
):
    # Tạo sản phẩm
    product_data = vars(product_in)
    product = Product(**product_data)
    db.add(product)
    db.commit()
    db.refresh(product)

    # print(f"Product created with ID {product.maSanPham}")

    # Upload và lưu nhiều hình ảnh
    if images:
        for idx, image in enumerate(images):
            if not image.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail=f"File {image.filename} không phải ảnh")
            contents = await image.read()
            kind = filetype.guess(contents)
            if not kind or not kind.mime.startswith("image/"):
                raise HTTPException(status_code=400, detail=f"Định dạng ảnh không hợp lệ: {image.filename}")
            if len(contents) > 5 * 1024 * 1024:
                raise HTTPException(status_code=413, detail=f"Ảnh quá lớn (tối đa 5MB): {image.filename}")
            
            print(f"Uploading {image.filename} to Cloudinary...")

            try:
                result = cloudinary.uploader.upload(
                    contents,
                    folder="products",
                    use_filename=True,
                    unique_filename=False,
                    overwrite=False
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Upload ảnh thất bại: {image.filename} - {str(e)}")

            # Lưu ảnh vào DB
            image_db = Image(
                duongDanAnh=result["secure_url"],
                maAnhClound=result["public_id"],
                moTa=product_in.moTa,
                laAnhChinh=1 if idx == 0 else 0,
                maSanPham=product.maSanPham
            )
            db.add(image_db)

        db.commit()
        db.refresh(product)

    return product

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
