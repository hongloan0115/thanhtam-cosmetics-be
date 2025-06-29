# Đã tạo ở bước trước
from dotenv import load_dotenv
import hmac, hashlib, urllib.parse
from datetime import datetime
from app.core.config import settings

load_dotenv()

def generate_vnpay_payment_url(order_id: int, amount: float, order_desc="Thanh toán đơn hàng"):
    vnp_Params = {
        "vnp_Version": "2.1.0",
        "vnp_Command": "pay",
        "vnp_TmnCode": settings.VNPAY_TMN_CODE,
        "vnp_Amount": str(int(amount * 100)),
        "vnp_CurrCode": "VND",
        "vnp_TxnRef": str(order_id),
        "vnp_OrderInfo": order_desc,
        "vnp_OrderType": "other",
        "vnp_Locale": "vn",
        "vnp_ReturnUrl": f"{settings.BACKEND_URL}/api/orders/vnpay-return",
        "vnp_IpAddr": "127.0.0.1",
        "vnp_CreateDate": datetime.now().strftime("%Y%m%d%H%M%S")
    }

    sorted_keys = sorted(vnp_Params.keys())
    query_string = ''
    hash_data = ''

    for key in sorted_keys:
        encoded_value = urllib.parse.quote_plus(vnp_Params[key])
        query_string += f"{key}={encoded_value}&"
        hash_data += f"{key}={encoded_value}&"

    query_string = query_string.rstrip("&")
    hash_data = hash_data.rstrip("&")
    secure_hash = hmac.new(settings.VNPAY_HASH_SECRET.encode(), hash_data.encode(), hashlib.sha512).hexdigest()
    return f"{settings.VNPAY_URL}?{query_string}&vnp_SecureHash={secure_hash}"
