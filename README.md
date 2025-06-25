# TỔNG QUAN DỰ ÁN

1.  Chức năng người dùng (khách hàng)
    👤 Tài khoản khách hàng - LUỒNG 01

        - Đăng ký/Đăng nhập

        - Cập nhật thông tin cá nhân

        - Xem lịch sử mua hàng

        Đổi mật khẩu (CHƯA LÀM)

        Quên mật khẩu (gửi email khôi phục) (CHƯA LÀM)

    🛍️ Mua sắm - LUỒNG 04

        - Xem danh sách sản phẩm (theo danh mục, theo thương hiệu)

        - Tìm kiếm sản phẩm (theo tên)

        - Lọc sản phẩm (theo giá, đánh giá, loại sản phẩm, thương hiệu…)

        - Xem chi tiết sản phẩm (hình ảnh, mô tả, giá, đánh giá, hướng dẫn sử dụng, thành phần…)

        - Thêm sản phẩm vào giỏ hàng

        - Cập nhật, xóa sản phẩm trong giỏ hàng

        - Áp dụng mã giảm giá (nếu có) (CHƯA LÀM)

        - Tính tổng tiền đơn hàng

    📦 Đặt hàng và thanh toán - LUỒNG 05

        - Tạo đơn hàng

        - Nhập thông tin giao hàng (tên, số điện thoại, địa chỉ…)

        - Chọn phương thức thanh toán:

            + Thanh toán khi nhận hàng (COD)

            + Chuyển khoản ngân hàng

            + Thanh toán online (VNPay, Momo, ZaloPay…)

        - Xác nhận đơn hàng qua email/SMS (CHƯA LÀM)

        - Theo dõi trạng thái đơn hàng (chờ xử lý, đang giao, đã giao, đã hủy)

    💬 Đánh giá & phản hồi

        Đánh giá sản phẩm (sao, bình luận)

        Gửi phản hồi/chăm sóc khách hàng

        Hệ thống FAQ (Câu hỏi thường gặp)

        Gửi liên hệ trực tiếp (form "Liên hệ chúng tôi")

    🤖 Chatbot AI tư vấn sản phẩm

        Tư vấn chọn sản phẩm phù hợp theo loại da, nhu cầu

        Trả lời câu hỏi thường gặp (giao hàng, đổi trả, cách sử dụng...)

        Gợi ý sản phẩm theo thương hiệu, vấn đề da

        Hướng dẫn đặt hàng và kiểm tra đơn hàng

        Hoạt động 24/7, hỗ trợ bằng tiếng Việt

        Có thể tích hợp chuyển tiếp đến nhân viên hỗ trợ

2.  Chức năng quản trị (Admin/cửa hàng)
    👥 Quản lý khách hàng - LUỒNG 02

        - Xem danh sách người dùng

        - Khóa/mở tài khoản người dùng

        - Xem lịch sử mua hàng của khách (CHƯA XONG)

    🗃️ Quản lý sản phẩm - LUỒNG 03

        - Thêm/sửa/xóa sản phẩm

        - Quản lý danh mục sản phẩm (dưỡng da, trang điểm, chăm sóc tóc…)

        - Quản lý thương hiệu

        - Quản lý số lượng tồn kho:

            + Tự động cập nhật tồn kho sau mỗi đơn hàng thành công

        - Cập nhật trạng thái sản phẩm (còn hàng, hết hàng)

            + Tự dộng cập nhật trạng thái mỗi khi sản phẩm sắp hết hàng

        - Tùy chọn hiển thị (nổi bật, khuyến mãi…) (CHƯA LÀM)

    💰 Quản lý đơn hàng - LUỒNG 06

        - Xem danh sách đơn hàng

        - Xem chi tiết từng đơn hàng

        - Xác nhận/thay đổi trạng thái đơn hàng

        Gửi email xác nhận cho khách

        In hóa đơn

    📢 Quản lý khuyến mãi

        Tạo mã giảm giá (mã code, giảm % hoặc số tiền)

        Cài đặt điều kiện áp dụng mã

        Quản lý các chương trình khuyến mãi (giảm giá theo sản phẩm, combo, flash sale…)

    📊 Báo cáo - Thống kê

        Doanh thu theo ngày/tháng/năm

        Sản phẩm bán chạy

        Tình trạng tồn kho

        Lượt truy cập website

        Đơn hàng theo trạng thái

3.  Chức năng bổ sung (tăng trải nghiệm người dùng)
    📰 Blog / Tin tức
    Cập nhật các bài viết liên quan đến làm đẹp, hướng dẫn chăm sóc da

        Review sản phẩm

        Mẹo sử dụng mỹ phẩm

    💌 Đăng ký nhận bản tin
    Gửi email marketing (giảm giá, sản phẩm mới…)

    🔐 Bảo mật và hiệu năng
    Giao diện thân thiện với thiết bị di động (responsive)

        HTTPS/SSL bảo mật

        Chống spam, bảo vệ thông tin người dùng

4.  Chức năng kỹ thuật (Back-end + DevOps)
    Quản lý phân quyền (Admin, nhân viên, khách hàng)

    Sao lưu dữ liệu định kỳ

    Hệ thống log lỗi và giám sát

    Tối ưu SEO

    Tích hợp Google Analytics, Facebook Pixel

# Cài thư viện

pip install -r requirements.txt

# Chạy dự án

uvicorn app.main:app --reload

pip freeze > requirements.txt
