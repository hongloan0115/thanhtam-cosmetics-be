from pydantic_settings import BaseSettings
from fastapi_mail import ConnectionConfig

class DBSettings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    MYSQL_PUBLIC_URL: str

    class Config:
        env_file = ".env"
        extra = "allow"

class MailSettings(BaseSettings):
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_TLS: bool
    MAIL_SSL: bool
    TEMPLATE_FOLDER: str

    class Config:
        env_file = ".env"
        extra = "allow"

class Settings(BaseSettings):
    db: DBSettings = DBSettings()
    mail: MailSettings = MailSettings()

    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int

    CLOUD_NAME: str
    API_KEY: str
    API_SECRET: str

    VNPAY_TMN_CODE: str
    VNPAY_HASH_SECRET: str
    VNPAY_URL: str

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    
    FRONTEND_URL: str
    BACKEND_URL: str
    
    OPENAI_API_KEY: str
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail.MAIL_USERNAME,
    MAIL_PASSWORD=settings.mail.MAIL_PASSWORD,
    MAIL_FROM=settings.mail.MAIL_FROM,
    MAIL_PORT=settings.mail.MAIL_PORT,
    MAIL_SERVER=settings.mail.MAIL_SERVER,
    MAIL_FROM_NAME=settings.mail.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.mail.MAIL_TLS,
    MAIL_SSL_TLS=settings.mail.MAIL_SSL,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=settings.mail.TEMPLATE_FOLDER,
)
