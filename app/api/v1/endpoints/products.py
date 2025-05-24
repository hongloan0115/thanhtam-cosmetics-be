import logging
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.core.security import get_current_admin
from app.models.product import Product
from app.models.image import Image
from app.crud import product as crud_product
from app.schemas.product import ProductUpdate, ProductOut, ProductCreateForm, ProductUpdateForm
from app.schemas.image import ImageOut
import cloudinary
import cloudinary.uploader
import filetype
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Thiết lập Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUD_NAME,
    api_key=settings.API_KEY,
    api_secret=settings.API_SECRET
)

@router.get("/", response_model=list[ProductOut])
def read_products(db: Session = Depends(get_db)):
    logger.info("Đang lấy danh sách sản phẩm")
    products = crud_product.get_products(db)
    result = []
    for product in products:
        main_images = [img for img in product.hinhAnh if img.laAnhChinh == 1]
        product_out = ProductOut.from_orm(product)
        product_out.hinhAnh = [ImageOut.from_orm(main_images[0])] if main_images else []
        result.append(product_out)
    logger.info(f"Đã trả về {len(result)} sản phẩm")
    return result

@router.get("/{product_id}", response_model=ProductOut)
def read_product(product_id: int, db: Session = Depends(get_db)):
    logger.info(f"Đang lấy thông tin sản phẩm với ID: {product_id}")
    product = crud_product.get_product_by_id(db, product_id)
    if not product:
        logger.warning(f"Sản phẩm với ID {product_id} không tồn tại")
        raise HTTPException(status_code=404, detail="Product not found")
    product_out = ProductOut.from_orm(product)
    product_out.hinhAnh = [ImageOut.from_orm(img) for img in product.hinhAnh] if product.hinhAnh else []
    logger.info(f"Đã lấy thành công sản phẩm với ID: {product_id}")
    return product_out

@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreateForm = Depends(),
    images: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin)
):
    logger.info(f"Tạo sản phẩm mới: {product_in.tenSanPham}")
    product_data = vars(product_in)
    product = Product(**product_data)
    db.add(product)
    db.commit()
    db.refresh(product)
    logger.info(f"Đã tạo sản phẩm với ID: {product.maSanPham}")

    if images:
        logger.info(f"Đang upload {len(images)} ảnh cho sản phẩm ID: {product.maSanPham}")
        for idx, image in enumerate(images):
            if not image.content_type.startswith("image/"):
                logger.warning(f"File {image.filename} không phải là ảnh")
                raise HTTPException(status_code=400, detail=f"File {image.filename} không phải ảnh")
            contents = await image.read()
            kind = filetype.guess(contents)
            if not kind or not kind.mime.startswith("image/"):
                logger.warning(f"Ảnh không hợp lệ: {image.filename}")
                raise HTTPException(status_code=400, detail=f"Định dạng ảnh không hợp lệ: {image.filename}")
            if len(contents) > 5 * 1024 * 1024:
                logger.warning(f"Ảnh quá lớn: {image.filename}")
                raise HTTPException(status_code=413, detail=f"Ảnh quá lớn (tối đa 5MB): {image.filename}")

            logger.info(f"Uploading {image.filename} to Cloudinary...")

            try:
                result = cloudinary.uploader.upload(
                    contents,
                    folder="products",
                    use_filename=True,
                    unique_filename=True,
                    overwrite=False
                )
                logger.info(f"Upload thành công: {image.filename}")
            except Exception as e:
                logger.error(f"Lỗi khi upload ảnh {image.filename}: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Upload ảnh thất bại: {image.filename} - {str(e)}")

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
        logger.info(f"Đã lưu {len(images)} ảnh vào database cho sản phẩm ID: {product.maSanPham}")

    return product

@router.put("/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: int,
    product_in: ProductUpdateForm = Depends(),
    images: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin)
):
    logger.info(f"Cập nhật sản phẩm ID: {product_id}")

    # Cập nhật thông tin sản phẩm
    product_data = {k: v for k, v in vars(product_in).items() if k != "keep_image_ids" and v is not None}
    product = crud_product.update_product(db, product_id, product_data)
    if not product:
        logger.warning(f"Không tìm thấy sản phẩm để cập nhật: ID {product_id}")
        raise HTTPException(status_code=404, detail="Product not found")

    # Xử lý cập nhật hình ảnh
    keep_image_ids = []
    if product_in.keep_image_ids:
        try:
            keep_image_ids = [int(i) for i in product_in.keep_image_ids.split(",") if i.strip().isdigit()]
        except Exception as e:
            logger.warning(f"Lỗi khi parse keep_image_ids: {str(e)}")
            raise HTTPException(status_code=400, detail="keep_image_ids không hợp lệ")

    # Xóa ảnh không nằm trong danh sách giữ lại
    current_images = db.query(Image).filter(Image.maSanPham == product_id).all()
    for img in current_images:
        if img.maHinhAnh not in keep_image_ids:
            try:
                cloudinary.uploader.destroy(img.maAnhClound)
            except Exception as e:
                logger.warning(f"Lỗi khi xóa ảnh trên Cloudinary: {img.maAnhClound} - {str(e)}")
            db.delete(img)
    db.commit()

    # Upload và lưu ảnh mới (nếu có)
    if images:
        logger.info(f"Đang upload {len(images)} ảnh mới cho sản phẩm ID: {product_id}")
        for idx, image in enumerate(images):
            if not image.content_type.startswith("image/"):
                logger.warning(f"File {image.filename} không phải là ảnh")
                raise HTTPException(status_code=400, detail=f"File {image.filename} không phải ảnh")
            contents = await image.read()
            kind = filetype.guess(contents)
            if not kind or not kind.mime.startswith("image/"):
                logger.warning(f"Ảnh không hợp lệ: {image.filename}")
                raise HTTPException(status_code=400, detail=f"Định dạng ảnh không hợp lệ: {image.filename}")
            if len(contents) > 5 * 1024 * 1024:
                logger.warning(f"Ảnh quá lớn: {image.filename}")
                raise HTTPException(status_code=413, detail=f"Ảnh quá lớn (tối đa 5MB): {image.filename}")

            logger.info(f"Uploading {image.filename} to Cloudinary...")

            try:
                result = cloudinary.uploader.upload(
                    contents,
                    folder="products",
                    use_filename=True,
                    unique_filename=True,
                    overwrite=False
                )
                logger.info(f"Upload thành công: {image.filename}")
            except Exception as e:
                logger.error(f"Lỗi khi upload ảnh {image.filename}: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Upload ảnh thất bại: {image.filename} - {str(e)}")

            image_db = Image(
                duongDanAnh=result["secure_url"],
                maAnhClound=result["public_id"],
                moTa=product.moTa,
                laAnhChinh=0,  # Có thể cập nhật logic chọn ảnh chính nếu cần
                maSanPham=product.maSanPham
            )
            db.add(image_db)
        db.commit()

    # Đảm bảo chỉ có 1 ảnh chính, nếu không có thì đặt ảnh đầu tiên làm ảnh chính
    images_in_db = db.query(Image).filter(Image.maSanPham == product_id).all()
    if images_in_db and not any(img.laAnhChinh == 1 for img in images_in_db):
        images_in_db[0].laAnhChinh = 1
        db.commit()

    logger.info(f"Đã cập nhật sản phẩm ID: {product_id} và hình ảnh liên quan")
    # Lấy lại sản phẩm đã cập nhật kèm ảnh
    product = crud_product.get_product_by_id(db, product_id)
    product_out = ProductOut.from_orm(product)
    product_out.hinhAnh = [ImageOut.from_orm(img) for img in product.hinhAnh] if product.hinhAnh else []
    return product_out

@router.delete("/{product_id}", response_model=ProductOut)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin)
):
    logger.info(f"Xóa sản phẩm ID: {product_id}")
    product = crud_product.delete_product(db, product_id)
    if not product:
        logger.warning(f"Không tìm thấy sản phẩm để xóa: ID {product_id}")
        raise HTTPException(status_code=404, detail="Product not found")
    logger.info(f"Đã xóa sản phẩm ID: {product_id}")
    return product
