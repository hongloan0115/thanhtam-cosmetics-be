from app.core.logger import get_logger
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.product import Product
from app.models.category import Category

logger = get_logger(__name__)

def get_products(db: Session):
    logger.info("Fetching all products")
    return db.query(Product).filter(Product.daXoa == False).all()

def get_product_by_id(db: Session, product_id: int):
    logger.info(f"Fetching product by id: {product_id}")
    return db.query(Product).filter(Product.maSanPham == product_id, Product.daXoa == False).first()

def search_products_by_name(db: Session, name: str):
    """Tìm kiếm sản phẩm theo tên (ilike)"""
    logger.info(f"Searching products by name: {name}")
    return db.query(Product).filter(
        Product.tenSanPham.ilike(f"%{name}%"),
        Product.daXoa == False
    ).all()

def filter_products(
    db: Session,
    maDanhMuc: int = None,
    giaMin: float = None,
    giaMax: float = None,
    trangThai: bool = None,
    thuongHieu: list = None
):
    """Lọc sản phẩm theo nhiều điều kiện: mã danh mục, giá bán, trạng thái, danh sách thương hiệu"""
    logger.info(
        f"Filtering products with maDanhMuc={maDanhMuc}, giaMin={giaMin}, giaMax={giaMax}, "
        f"trangThai={trangThai}, thuongHieu={thuongHieu}"
    )
    query = db.query(Product).filter(Product.daXoa == False)
    if maDanhMuc is not None:
        query = query.filter(Product.maDanhMuc == maDanhMuc)
    if giaMin is not None:
        query = query.filter(Product.giaBan >= giaMin)
    if giaMax is not None:
        query = query.filter(Product.giaBan <= giaMax)
    if trangThai is not None:
        query = query.filter(Product.trangThai == trangThai)
    if thuongHieu:
        query = query.filter(Product.maThuongHieu.in_(thuongHieu))
    return query.all()

def create_product(db: Session, product: Product):
    logger.info(f"Creating product: {product.tenSanPham}")
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def update_product(db: Session, product_id: int, product_data: dict):
    logger.info(f"Updating product id: {product_id} with data: {product_data}")
    product = db.query(Product).filter(Product.maSanPham == product_id).first()
    if product:
        for key, value in product_data.items():
            setattr(product, key, value)
        db.commit()
        db.refresh(product)
    return product

def delete_product(db: Session, product_id: int):
    logger.info(f"Deleting product id: {product_id}")
    product = db.query(Product).filter(Product.maSanPham == product_id, Product.daXoa == False).first()
    if product:
        product.daXoa = True
        db.commit()
        db.refresh(product)
    return product

def search_products(
    db: Session,
    min_price: float = None,
    max_price: float = None,
    keywords: list = None,
):
    logger.info(f"Searching products with min_price={min_price}, max_price={max_price}, keywords={keywords}")
    query = db.query(Product).join(Category, Product.maDanhMuc == Category.maDanhMuc, isouter=True)

    # Lọc theo khoảng giá
    if min_price is not None:
        query = query.filter(Product.giaBan >= min_price)
    if max_price is not None:
        query = query.filter(Product.giaBan <= max_price)

    # Lọc theo từ khóa (áp dụng cho các trường text)
    if keywords:
        like_clauses = []
        for kw in keywords:
            like_pattern = f"%{kw}%"
            like_clauses.extend([
                Product.tenSanPham.ilike(like_pattern),
                Product.moTa.ilike(like_pattern),
                Category.tenDanhMuc.ilike(like_pattern),
            ])
        query = query.filter(or_(*like_clauses))

    return query.all()

def get_products_for_context(db: Session, keywords: list, limit: int = 5):
    """Lấy thông tin sản phẩm để cung cấp context cho AI"""
    logger.info(f"Getting products for context with keywords: {keywords}")
    
    if not keywords:
        return ""
    
    query = db.query(Product).join(Category)
    
    # Tìm kiếm theo từ khóa
    like_clauses = []
    for kw in keywords:
        like_pattern = f"%{kw}%"
        like_clauses.extend([
            Product.tenSanPham.ilike(like_pattern),
            Product.moTa.ilike(like_pattern),
            Category.tenDanhMuc.ilike(like_pattern),
        ])
    
    if like_clauses:
        query = query.filter(or_(*like_clauses))
    
    products = query.limit(limit).all()
    
    if not products:
        return ""
    
    # Tạo context string
    context_parts = []
    for product in products:
        context_parts.append(
            f"- {product.tenSanPham}: Giá {product.giaBan:,}đ. "
            f"Mô tả: {product.moTa or 'Chưa có mô tả'}. "
            f"Danh mục: {product.category.tenDanhMuc if product.category else 'Chưa phân loại'}"
        )
    
    return "\n".join(context_parts)

def check_products_exist(
    db: Session,
    keywords: list = None,
    min_price: float = None,
    max_price: float = None
):
    """Kiểm tra sự tồn tại và đếm số lượng sản phẩm mà không lấy toàn bộ dữ liệu"""
    logger.info(f"Checking product existence with keywords={keywords}, min_price={min_price}, max_price={max_price}")
    
    query = db.query(Product).join(Category)

    # Lọc theo khoảng giá
    if min_price is not None:
        query = query.filter(Product.giaBan >= min_price)
    if max_price is not None:
        query = query.filter(Product.giaBan <= max_price)

    # Lọc theo từ khóa
    if keywords:
        like_clauses = []
        for kw in keywords:
            like_pattern = f"%{kw}%"
            like_clauses.extend([
                Product.tenSanPham.ilike(like_pattern),
                Product.moTa.ilike(like_pattern),
                Category.tenDanhMuc.ilike(like_pattern),
            ])
        query = query.filter(or_(*like_clauses))

    count = query.count()
    logger.info(f"Found {count} products matching criteria")
    
    return {
        "count": count,
        "has_products": count > 0
    }

def get_basic_products_info(
    db: Session,
    keywords: list = None,
    min_price: float = None,
    max_price: float = None,
    limit: int = 5
):
    """Lấy thông tin cơ bản của sản phẩm bao gồm ID, tên, giá và hình ảnh"""
    logger.info(f"Getting basic product info with keywords={keywords}")
    
    query = db.query(Product).join(Category, Product.maDanhMuc == Category.maDanhMuc, isouter=True)

    # Áp dụng các filter tương tự
    if min_price is not None:
        query = query.filter(Product.giaBan >= min_price)
    if max_price is not None:
        query = query.filter(Product.giaBan <= max_price)

    if keywords:
        like_clauses = []
        for kw in keywords:
            like_pattern = f"%{kw}%"
            like_clauses.extend([
                Product.tenSanPham.ilike(like_pattern),
                Product.moTa.ilike(like_pattern),
                Category.tenDanhMuc.ilike(like_pattern),
            ])
        query = query.filter(or_(*like_clauses))

    products = query.limit(limit).all()
    
    result = []
    for p in products:
        # Lấy hình ảnh đầu tiên nếu có
        image_url = None
        if p.hinhAnh and len(p.hinhAnh) > 0:
            image_url = p.hinhAnh[0].duongDan
        
        result.append({
            "maSanPham": p.maSanPham,
            "tenSanPham": p.tenSanPham,
            "giaBan": p.giaBan,
            "hinhAnh": image_url,
            "link": f"/products/{p.maSanPham}"
        })
    
    return result

def get_products_with_details(
    db: Session,
    min_price: float = None,
    max_price: float = None,
    keywords: list = None,
    limit: int = 10
):
    """Lấy sản phẩm với đầy đủ thông tin để hiển thị cho người dùng"""
    logger.info(f"Getting products with details")
    
    query = db.query(Product).join(Category, Product.maDanhMuc == Category.maDanhMuc, isouter=True)

    # Lọc theo khoảng giá
    if min_price is not None:
        query = query.filter(Product.giaBan >= min_price)
    if max_price is not None:
        query = query.filter(Product.giaBan <= max_price)

    # Lọc theo từ khóa
    if keywords:
        like_clauses = []
        for kw in keywords:
            like_pattern = f"%{kw}%"
            like_clauses.extend([
                Product.tenSanPham.ilike(like_pattern),
                Product.moTa.ilike(like_pattern),
                Category.tenDanhMuc.ilike(like_pattern),
            ])
        query = query.filter(or_(*like_clauses))

    products = query.limit(limit).all()
    
    result = []
    for p in products:
        # Lấy hình ảnh đầu tiên nếu có
        image_url = None
        if p.hinhAnh and len(p.hinhAnh) > 0:
            image_url = p.hinhAnh[0].duongDan
        
        result.append({
            "maSanPham": p.maSanPham,
            "tenSanPham": p.tenSanPham,
            "giaBan": p.giaBan,
            "hinhAnh": image_url,
            "link": f"/products/{p.maSanPham}"
        })
    
    return result

