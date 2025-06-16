from fastapi import APIRouter, Depends, Request, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.responses import RedirectResponse

from app.schemas.order import OrderCreate, OrderCheckoutResponse, Order, OrderUpdate, OrderStatusEnum
from app.schemas.order_detail import OrderDetailCreate
from app.crud import order as crud_order
from app.crud import order_detail as crud_order_detail
from app.db.database import get_db
from app.models.product import Product
from app.models.cart_item import CartItem, TrangThaiGioHangEnum
from app.models.order import Order as OrderModel, TrangThaiDonHangEnum, TrangThaiThanhToanEnum
import urllib.parse
import hashlib
import hmac
import enum
from app.core.security import get_current_admin

from app.db.database import get_db
from app.models.order import Order as Order
from app.models.order_detail import OrderDetail
from app.schemas.order import OrderCreate, OrderCheckoutResponse, OrderStatusEnum, OrderStatusUpdate, OrderOutForAdmin
from app.schemas.order_detail import OrderDetailCreate
from app.utils.vnpay import generate_vnpay_payment_url
from app.core.logger import get_logger
from app.core.config import settings
from app.schemas.order import OrderOut

logger = get_logger(__name__)

router = APIRouter()

class TrangThaiThanhToanEnum(enum.Enum):
    CHUATHANHTOAN = "CHƯA THANH TOÁN"
    DATHANHTOAN = "ĐÃ THANH TOÁN"

@router.get("/admin/all", response_model=List[OrderOutForAdmin])
def admin_get_all_orders(db: Session = Depends(get_db), admin_user=Depends(get_current_admin)):
    """
    Admin: Lấy tất cả đơn hàng.
    """
    orders = db.query(OrderModel).order_by(OrderModel.ngayDat.desc()).all()
    return orders

@router.get("/admin/order/{maDonHang}", response_model=OrderOutForAdmin)
def admin_get_order_detail(maDonHang: int, db: Session = Depends(get_db), admin_user=Depends(get_current_admin)):
    """
    Admin: Xem chi tiết đơn hàng theo mã.
    """
    order = db.query(OrderModel).filter(OrderModel.maDonHang == maDonHang).first()
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")
    return order

@router.patch("/admin/order/update-status/{maDonHang}", response_model=OrderOutForAdmin)
def admin_update_order_status(
    maDonHang: int,
    trangThaiCapNhat: OrderStatusUpdate = Body(...),
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin)
):
    """
    Admin: Cập nhật trạng thái đơn hàng.
    """
    order = db.query(OrderModel).filter(OrderModel.maDonHang == maDonHang).first()
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")
    order.trangThai = trangThaiCapNhat.trangThai
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

@router.post("/checkout", response_model=OrderCheckoutResponse)
def create_order(
    order_data: OrderCreate,
    order_details: list[OrderDetailCreate],
    db: Session = Depends(get_db)
):
    # 1. Tạo đơn hàng
    db_order = Order(
        maNguoiDung=order_data.maNguoiDung,
        diaChiChiTiet=order_data.diaChiChiTiet,
        tinhThanh=order_data.tinhThanh,
        quanHuyen=order_data.quanHuyen,
        phuongXa=order_data.phuongXa,
        maPhuongThuc=order_data.maPhuongThuc,
        tongTien=order_data.tongTien,
        trangThai=order_data.trangThai.value,
        ghiChu=order_data.ghiChu,
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # 2. Tạo chi tiết đơn hàng & cập nhật tồn kho sản phẩm
    for detail in order_details:
        db_detail = OrderDetail(
            maDonHang=db_order.maDonHang,
            maSanPham=detail.maSanPham,
            soLuong=detail.soLuong,
            donGia=detail.donGia,
            tongTien=detail.tongTien
        )
        db.add(db_detail)

        # Trừ số lượng tồn kho sản phẩm
        product = db.query(Product).filter(Product.maSanPham == detail.maSanPham).first()
        if product:
            if product.soLuongTonKho is not None and product.soLuongTonKho >= detail.soLuong:
                product.soLuongTonKho -= detail.soLuong
            else:
                raise HTTPException(status_code=400, detail=f"Sản phẩm {product.tenSanPham} không đủ số lượng tồn kho")
            db.add(product)

    db.commit()

    # 3. Xóa các sản phẩm đã đặt khỏi giỏ hàng của người dùng
    product_ids = [detail.maSanPham for detail in order_details]
    db.query(CartItem).filter(
        CartItem.maNguoiDung == order_data.maNguoiDung,
        CartItem.maSanPham.in_(product_ids)
    ).delete(synchronize_session=False)
    db.commit()

    # 4. Tạo URL VNPay nếu phương thức thanh toán là VNPay (giả sử mã là 2)
    payment_url = None
    if db_order.maPhuongThuc == 2:
        payment_url = generate_vnpay_payment_url(db_order.maDonHang, float(db_order.tongTien))

    return OrderCheckoutResponse(
        maDonHang=db_order.maDonHang,
        payment_url=payment_url
    )

@router.get("/vnpay-return")
async def vnpay_return(request: Request):
    # Bước 1: Lấy tất cả query params, loại bỏ vnp_SecureHash và vnp_SecureHashType
    input_data = dict(request.query_params)
    vnp_secure_hash = input_data.pop("vnp_SecureHash", None)
    input_data.pop("vnp_SecureHashType", None)  # Có thể không cần thiết

    # Bước 2: Sắp xếp các tham số tăng dần theo key
    sorted_params = sorted(input_data.items())

    # Bước 3: Tạo lại chuỗi hash_data với urllib.parse.quote_plus()
    hash_data = ''
    for key, value in sorted_params:
        encoded_value = urllib.parse.quote_plus(value)
        hash_data += f"{key}={encoded_value}&"
    hash_data = hash_data.rstrip("&")

    # Bước 4: Tạo lại chữ ký
    computed_hash = hmac.new(settings.VNPAY_HASH_SECRET.encode(), hash_data.encode(), hashlib.sha512).hexdigest()

    # Bước 5: So sánh chữ ký
    if computed_hash == vnp_secure_hash:
        response_code = input_data.get("vnp_ResponseCode")
        txn_ref = input_data.get("vnp_TxnRef")

        frontend_url = "http://localhost:3000/payment-result"  # Đảm bảo biến này có trong config, ví dụ: "https://your-frontend.com/payment-result"
        if response_code == "00":
            # ✅ Thành công
            redirect_url = f"{frontend_url}?order_id={txn_ref}&status=success"
            return RedirectResponse(url=redirect_url)
        else:
            redirect_url = f"{frontend_url}?order_id={txn_ref}&status=fail&error_code={response_code}"
            return RedirectResponse(url=redirect_url)
    else:
        frontend_url = "http://localhost:3000/payment-result"
        redirect_url = f"{frontend_url}?status=fail&error=invalid_signature"
        return RedirectResponse(url=redirect_url)



# @router.get("/history/{maNguoiDung}", response_model=List[Order])
# def get_order_history(
#     maNguoiDung: int,
#     db: Session = Depends(get_db)
# ):
#     orders = db.query(OrderModel).filter(OrderModel.maNguoiDung == maNguoiDung).order_by(OrderModel.ngayDat.desc()).all()
#     return orders

# @router.put("/cancel/{maDonHang}", response_model=Order)
# def user_cancel_order(
#     maDonHang: int,
#     db: Session = Depends(get_db)
# ):
#     """
#     Người dùng hủy đơn hàng sau khi đặt thành công.
#     """
#     order = db.query(OrderModel).filter(OrderModel.maDonHang == maDonHang).first()
#     if not order:
#         raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")
#     if order.trangThai == OrderStatusEnum.DABIHUY.value:
#         raise HTTPException(status_code=400, detail="Order already cancelled")
#     if order.trangThai == OrderStatusEnum.HOANTHANH.value:
#         raise HTTPException(status_code=400, detail="Order already completed")
#     order.trangThai = OrderStatusEnum.DABIHUY.value
#     db.add(order)
#     db.commit()
#     db.refresh(order)
#     return order

