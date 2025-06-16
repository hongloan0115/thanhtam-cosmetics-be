from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.core.security import get_current_admin
from app.models.product import Product, TrangThaiSanPham
from app.models.image import Image
from app.crud import product as crud_product
from app.schemas.product import ProductUpdate, ProductOut, ProductCreateForm, ProductUpdateForm
from app.schemas.image import ImageOut
from app.core.logger import get_logger
from app.utils import image as image_utils

logger = get_logger(__name__)

router = APIRouter()

# Cần phải đưa các route cố định như /search, /filter lên trên các route động /{product_id} 
# để tránh xung đột
@router.get("/search", response_model=list[ProductOut])
def search_products(
    q: str = Query(..., min_length=1, description="Tên sản phẩm cần tìm"),
    db: Session = Depends(get_db)
):
    logger.info(f"Tìm kiếm sản phẩm với tên: {q}")
    products = crud_product.search_products_by_name(db, q)
    result = []
    for product in products:
        main_images = [img for img in product.hinhAnh if img.laAnhChinh == 1]
        product_out = ProductOut.from_orm(product)
        product_out.hinhAnh = [ImageOut.from_orm(main_images[0])] if main_images else []
        result.append(product_out)
    logger.info(f"Đã tìm thấy {len(result)} sản phẩm phù hợp với '{q}'")
    return result

@router.get("/filter", response_model=list[ProductOut])
def filter_products(
    maDanhMuc: int = Query(None, description="Mã danh mục"),
    giaMin: int = Query(None, description="Giá tối thiểu"),
    giaMax: int = Query(None, description="Giá tối đa"),
    trangThai: bool = Query(None, description="Trạng thái sản phẩm"),
    thuongHieu: List[str] = Query(None, description="Danh sách thương hiệu (có thể truyền nhiều giá trị)"),
    db: Session = Depends(get_db)
):
    logger.info(
        f"Lọc sản phẩm với các điều kiện: maDanhMuc={maDanhMuc}, giaMin={giaMin}, giaMax={giaMax}, "
        f"trangThai={trangThai}, thuongHieu={thuongHieu}"
    )
    products = crud_product.filter_products(
        db,
        maDanhMuc=maDanhMuc,
        giaMin=giaMin,
        giaMax=giaMax,
        trangThai=trangThai,
        thuongHieu=thuongHieu
    )
    result = []
    for product in products:
        main_images = [img for img in product.hinhAnh if img.laAnhChinh == 1]
        product_out = ProductOut.from_orm(product)
        product_out.hinhAnh = [ImageOut.from_orm(main_images[0])] if main_images else []
        result.append(product_out)
    logger.info(f"Đã lọc được {len(result)} sản phẩm")
    return result

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

    # Kiểm tra số lượng để cập nhật trạng thái sản phẩm cho đúng
    so_luong = product_data.get("soLuongTonKho")
    if so_luong is not None:
        if so_luong == 0:
            product_data["trangThai"] = TrangThaiSanPham.HETHANG
        elif so_luong < 5:
            product_data["trangThai"] = TrangThaiSanPham.SAPHET
        else:
            # Nếu trạng thái không được truyền vào, mặc định là ĐANG BÁN
            if not product_data.get("trangThai"):
                product_data["trangThai"] = TrangThaiSanPham.DANGBAN

    product = Product(**product_data)
    db.add(product)
    db.commit()
    db.refresh(product)
    logger.info(f"Đã tạo sản phẩm với ID: {product.maSanPham}")

    if images:
        logger.info(f"Đang upload {len(images)} ảnh cho sản phẩm ID: {product.maSanPham}")
        for idx, image in enumerate(images):
            contents = await image_utils.validate_image_uploadfile(image)
            logger.info(f"Uploading {image.filename} to Cloudinary...")
            result = image_utils.upload_image_to_cloudinary(contents, folder="products")
            logger.info(f"Upload thành công: {image.filename}")
            image_db = Image(
                duongDan=result["secure_url"],
                maAnhClound=result["public_id"],
                moTa=product_in.moTa,
                laAnhChinh=True if idx == 0 else False,
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
            image_utils.delete_image_from_cloudinary(img.maAnhClound)
            db.delete(img)
    db.commit()

    # Upload và lưu ảnh mới (nếu có)
    if images:
        logger.info(f"Đang upload {len(images)} ảnh mới cho sản phẩm ID: {product_id}")
        for idx, image in enumerate(images):
            contents = await image_utils.validate_image_uploadfile(image)
            logger.info(f"Uploading {image.filename} to Cloudinary...")
            result = image_utils.upload_image_to_cloudinary(contents, folder="products")
            logger.info(f"Upload thành công: {image.filename}")
            image_db = Image(
                duongDan=result["secure_url"],
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
