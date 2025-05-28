from fastapi import APIRouter, Depends, Request, HTTPException
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
import datetime

from app.db.database import get_db
from app.models.order import Order as Order
from app.models.order_detail import OrderDetail
from app.schemas.order import OrderCreate, OrderCheckoutResponse
from app.schemas.order_detail import OrderDetailCreate
from app.utils.vnpay import generate_vnpay_payment_url
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)

router = APIRouter()

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
        trangThaiThanhToan="CHUATHANHTOAN"
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # 2. Tạo chi tiết đơn hàng
    for detail in order_details:
        db_detail = OrderDetail(
            maDonHang=db_order.maDonHang,
            maSanPham=detail.maSanPham,
            soLuong=detail.soLuong,
            donGia=detail.donGia,
            tongTien=detail.tongTien
        )
        db.add(db_detail)

    db.commit()

    # 3. Tạo URL VNPay nếu phương thức thanh toán là VNPay (giả sử mã là 2)
    payment_url = None
    if db_order.maPhuongThuc == 2:
        payment_url = generate_vnpay_payment_url(db_order.maDonHang, float(db_order.tongTien))

    return OrderCheckoutResponse(
        maDonHang=db_order.maDonHang,
        payment_url=payment_url
    )


# @router.get("/admin/all", response_model=List[Order])
# def get_all_orders_admin(
#     db: Session = Depends(get_db)
# ):
#     """
#     Lấy tất cả đơn hàng (dành cho admin).
#     """
#     orders = db.query(OrderModel).order_by(OrderModel.ngayDat.desc()).all()
#     return orders

# @router.put("/admin/update-status/{maDonHang}", response_model=Order)
# def admin_update_order_status(
#     maDonHang: int,
#     update_in: OrderUpdate,
#     db: Session = Depends(get_db)
# ):
#     """
#     Admin cập nhật trạng thái đơn hàng.
#     """
#     order = db.query(OrderModel).filter(OrderModel.maDonHang == maDonHang).first()
#     if not order:
#         raise HTTPException(status_code=404, detail="Order not found")
#     if update_in.trangThai:
#         order.trangThai = update_in.trangThai.value
#     if update_in.ghiChu is not None:
#         order.ghiChu = update_in.ghiChu
#     db.add(order)
#     db.commit()
#     db.refresh(order)
#     return order

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
#         raise HTTPException(status_code=404, detail="Order not found")
#     if order.trangThai == OrderStatusEnum.DABIHUY.value:
#         raise HTTPException(status_code=400, detail="Order already cancelled")
#     if order.trangThai == OrderStatusEnum.HOANTHANH.value:
#         raise HTTPException(status_code=400, detail="Order already completed")
#     order.trangThai = OrderStatusEnum.DABIHUY.value
#     db.add(order)
#     db.commit()
#     db.refresh(order)
#     return order

