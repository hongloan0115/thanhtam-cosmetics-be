from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, cast, Date
from datetime import date, timedelta
from app.db.database import get_db
from app.models.order import Order
from app.models.order_detail import OrderDetail
from app.models.product import Product
from app.models.category import Category
from app.models.user import User

router = APIRouter()

@router.get("/revenue/day")
def revenue_by_day(db: Session = Depends(get_db), year: int = None, month: int = None):
    """
    Thống kê doanh thu theo từng ngày trong tháng (hoặc tháng hiện tại nếu không truyền).
    """
    if not year or not month:
        today = date.today()
        year = year or today.year
        month = month or today.month
    results = (
        db.query(
            func.date(Order.ngayDat).label("day"),
            func.sum(Order.tongTien).label("revenue")
        )
        .filter(
            extract("year", Order.ngayDat) == year,
            extract("month", Order.ngayDat) == month,
            Order.trangThai != "ĐÃ BỊ HUỶ"
        )
        .group_by(func.date(Order.ngayDat))
        .order_by(func.date(Order.ngayDat))
        .all()
    )
    return [{"day": str(r.day), "revenue": float(r.revenue or 0)} for r in results]

@router.get("/revenue/month")
def revenue_by_month(db: Session = Depends(get_db), year: int = None):
    """
    Thống kê doanh thu theo từng tháng trong năm (hoặc năm hiện tại nếu không truyền).
    """
    if not year:
        year = date.today().year
    results = (
        db.query(
            extract("month", Order.ngayDat).label("month"),
            func.sum(Order.tongTien).label("revenue")
        )
        .filter(
            extract("year", Order.ngayDat) == year,
            Order.trangThai != "ĐÃ BỊ HUỶ"
        )
        .group_by(extract("month", Order.ngayDat))
        .order_by(extract("month", Order.ngayDat))
        .all()
    )
    return [{"month": int(r.month), "revenue": float(r.revenue or 0)} for r in results]

@router.get("/revenue/year")
def revenue_by_year(db: Session = Depends(get_db)):
    """
    Thống kê doanh thu theo từng năm.
    """
    results = (
        db.query(
            extract("year", Order.ngayDat).label("year"),
            func.sum(Order.tongTien).label("revenue")
        )
        .filter(Order.trangThai != "ĐÃ BỊ HUỶ")
        .group_by(extract("year", Order.ngayDat))
        .order_by(extract("year", Order.ngayDat))
        .all()
    )
    return [{"year": int(r.year), "revenue": float(r.revenue or 0)} for r in results]

@router.get("/bestsellers/chart")
def best_selling_products_chart(
    db: Session = Depends(get_db),
    limit: int = 5
):
    """
    API trả về dữ liệu sản phẩm bán chạy cho biểu đồ (dùng cho dashboard).
    Trả về: [{ name: <tên sản phẩm>, sales: <số lượng bán> }]
    """
    results = (
        db.query(
            Product.tenSanPham.label("name"),
            func.sum(OrderDetail.soLuong).label("sales")
        )
        .join(OrderDetail, Product.maSanPham == OrderDetail.maSanPham)
        .join(Order, Order.maDonHang == OrderDetail.maDonHang)
        .filter(Order.trangThai != "ĐÃ BỊ HUỶ")
        .group_by(Product.tenSanPham)
        .order_by(func.sum(OrderDetail.soLuong).desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "name": r.name,
            "sales": int(r.sales or 0)
        }
        for r in results
    ]

@router.get("/orders-by-status")
def orders_by_status(db: Session = Depends(get_db)):
    """
    Thống kê số lượng đơn hàng theo từng trạng thái.
    """
    results = (
        db.query(
            Order.trangThai,
            func.count(Order.maDonHang).label("count")
        )
        .group_by(Order.trangThai)
        .all()
    )
    return [
        {
            "trangThai": r.trangThai,
            "count": r.count
        }
        for r in results
    ]

@router.get("/dashboard/summary")
def dashboard_summary(
    db: Session = Depends(get_db),
    year: int = None,
    month: int = None
):
    """
    API tổng hợp cho dashboard: tổng doanh thu, đơn hàng, khách hàng, giá trị đơn hàng trung bình, tỉ lệ tăng so với tháng trước.
    """
    today = date.today()
    year = year or today.year
    month = month or today.month

    # Tháng trước
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year

    # Tổng doanh thu
    def get_revenue(y, m):
        return db.query(func.coalesce(func.sum(Order.tongTien), 0)).filter(
            extract("year", Order.ngayDat) == y,
            extract("month", Order.ngayDat) == m,
            Order.trangThai != "ĐÃ BỊ HUỶ"
        ).scalar() or 0

    revenue_this = float(get_revenue(year, month))
    revenue_prev = float(get_revenue(prev_year, prev_month))
    revenue_rate = ((revenue_this - revenue_prev) / revenue_prev * 100) if revenue_prev > 0 else (100 if revenue_this > 0 else 0)

    # Tổng đơn hàng (không tính đã huỷ)
    def get_orders_count(y, m):
        return db.query(func.count(Order.maDonHang)).filter(
            extract("year", Order.ngayDat) == y,
            extract("month", Order.ngayDat) == m,
            Order.trangThai != "ĐÃ BỊ HUỶ"
        ).scalar() or 0

    orders_this = get_orders_count(year, month)
    orders_prev = get_orders_count(prev_year, prev_month)
    orders_rate = ((orders_this - orders_prev) / orders_prev * 100) if orders_prev > 0 else (100 if orders_this > 0 else 0)

    # Số khách hàng mới trong tháng
    def get_new_customers(y, m):
        return db.query(func.count(User.maNguoiDung)).filter(
            extract("year", User.ngayTao) == y,
            extract("month", User.ngayTao) == m
        ).scalar() or 0

    customers_this = get_new_customers(year, month)
    customers_prev = get_new_customers(prev_year, prev_month)
    customers_rate = ((customers_this - customers_prev) / customers_prev * 100) if customers_prev > 0 else (100 if customers_this > 0 else 0)

    # Giá trị trung bình mỗi đơn hàng
    avg_this = revenue_this / orders_this if orders_this > 0 else 0
    avg_prev = revenue_prev / orders_prev if orders_prev > 0 else 0
    avg_rate = ((avg_this - avg_prev) / avg_prev * 100) if avg_prev > 0 else (100 if avg_this > 0 else 0)

    return {
        "revenue": {
            "total": revenue_this,
            "rate": revenue_rate
        },
        "orders": {
            "total": orders_this,
            "rate": orders_rate
        },
        "customers": {
            "total": customers_this,
            "rate": customers_rate
        },
        "average_order_value": {
            "value": avg_this,
            "rate": avg_rate
        }
    }

@router.get("/revenue/category-by-month")
def revenue_by_category_by_month(
    db: Session = Depends(get_db),
    year: int = None,
    month: int = None
):
    """
    API trả về dữ liệu doanh thu theo danh mục cho biểu đồ (dùng cho dashboard).
    Trả về: [{ name: <tên danh mục>, value: <tỉ lệ phần trăm doanh thu> }]
    """
    today = date.today()
    year = year or today.year
    month = month or today.month

    # Lấy tổng doanh thu tháng này (không tính đơn huỷ)
    total_revenue = (
        db.query(func.coalesce(func.sum(OrderDetail.tongTien), 0))
        .join(Order, Order.maDonHang == OrderDetail.maDonHang)
        .filter(
            extract("year", Order.ngayDat) == year,
            extract("month", Order.ngayDat) == month,
            Order.trangThai != "ĐÃ BỊ HUỶ"
        )
        .scalar()
    ) or 0

    # Lấy doanh thu từng danh mục
    results = (
        db.query(
            Category.tenDanhMuc.label("name"),
            func.coalesce(func.sum(OrderDetail.tongTien), 0).label("revenue")
        )
        .join(Product, Product.maDanhMuc == Category.maDanhMuc)
        .join(OrderDetail, OrderDetail.maSanPham == Product.maSanPham)
        .join(Order, Order.maDonHang == OrderDetail.maDonHang)
        .filter(
            extract("year", Order.ngayDat) == year,
            extract("month", Order.ngayDat) == month,
            Order.trangThai != "ĐÃ BỊ HUỶ"
        )
        .group_by(Category.tenDanhMuc)
        .all()
    )

    # Tính tỉ lệ phần trăm cho từng danh mục
    data = []
    for r in results:
        percent = (float(r.revenue) / total_revenue * 100) if total_revenue > 0 else 0
        data.append({
            "name": r.name,
            "value": round(percent, 2)
        })

    return data

@router.get("/sales-chart")
def sales_chart(
    db: Session = Depends(get_db),
    time_range: str = "daily"   # Đổi tên tham số từ range -> time_range
):
    """
    API trả về dữ liệu cho biểu đồ doanh số bán hàng:
    - daily: 7 ngày gần nhất
    - weekly: 4 tuần gần nhất
    - monthly: 12 tháng gần nhất
    Trả về: [{ name: <label>, sales: <doanh số> }]
    """
    today = date.today()

    if time_range == "daily":
        start_date = today - timedelta(days=6)
        results = (
            db.query(
                func.date(Order.ngayDat).label("name"),
                func.coalesce(func.sum(Order.tongTien), 0).label("sales")
            )
            .filter(
                Order.ngayDat >= start_date,
                Order.ngayDat <= today,
                Order.trangThai != "ĐÃ BỊ HUỶ"
            )
            .group_by(func.date(Order.ngayDat))
            .order_by(func.date(Order.ngayDat))
            .all()
        )
        # Đảm bảo đủ 7 ngày, kể cả ngày không có đơn
        data = []
        for i in range(7):
            d = start_date + timedelta(days=i)
            found = next((r for r in results if r.name == d), None)
            data.append({
                "name": d.strftime("%d/%m"),
                "sales": float(found.sales) if found else 0
            })
        return data

    elif time_range == "weekly":
        # Lấy 4 tuần gần nhất (tính từ thứ 2 đầu tuần)
        start_date = today - timedelta(days=today.weekday() + 27)
        end_date = today
        data = []
        for i in range(4):
            week_start = start_date + timedelta(days=i * 7)
            week_end = week_start + timedelta(days=6)
            sales = (
                db.query(func.coalesce(func.sum(Order.tongTien), 0))
                .filter(
                    cast(Order.ngayDat, Date) >= week_start,
                    cast(Order.ngayDat, Date) <= week_end,
                    Order.trangThai != "ĐÃ BỊ HUỶ"
                )
                .scalar()
            ) or 0
            data.append({
                "name": f"Tuần {i+1}",
                "sales": float(sales)
            })
        return data

    elif time_range == "monthly":
        # Lấy 12 tháng gần nhất
        data = []
        for i in range(12):
            m = (today.month - 11 + i - 1) % 12 + 1
            y = today.year if today.month - 11 + i > 0 else today.year - 1
            sales = (
                db.query(func.coalesce(func.sum(Order.tongTien), 0))
                .filter(
                    extract("year", Order.ngayDat) == y,
                    extract("month", Order.ngayDat) == m,
                    Order.trangThai != "ĐÃ BỊ HUỶ"
                )
                .scalar()
            ) or 0
            data.append({
                "name": f"T{m}",
                "sales": float(sales)
            })
        return data

    return []
