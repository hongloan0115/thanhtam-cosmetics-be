from fastapi_mail import FastMail, MessageSchema, MessageType
from app.core.config import conf

async def send_verification_email(email: str, code: str):
    message = MessageSchema(
        subject="Xác thực tài khoản",
        recipients=[email],
        template_body={"code": code},
        subtype=MessageType.html,
    )
    fm = FastMail(conf)
    await fm.send_message(message, template_name="verify_email.html")
