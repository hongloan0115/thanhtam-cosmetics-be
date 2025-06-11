from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import engine, Base
from app.init_data.init_roles import init_roles
from app.init_data.init_admin import init_admin

from app.api.v1.endpoints import auth
from app.api.v1.endpoints import google
from app.api.v1.endpoints import products
from app.api.v1.endpoints import users
from app.api.v1.endpoints import categories
from app.api.v1.endpoints import carts
from app.api.v1.endpoints import payment_methods
from app.api.v1.endpoints import orders
# from app.api.v1.endpoints import websocket

app = FastAPI(
    title="User Registration API",
    description="Đăng ký người dùng với xác thực email và vai trò mặc định là KHACHHANG",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

init_roles() 
init_admin()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(google.router, prefix="/api/auth/google", tags=["Google Auth"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(categories.router, prefix="/api/categories", tags=["Categories"])
app.include_router(carts.router, prefix="/api", tags=["Carts"])
app.include_router(payment_methods.router, prefix="/api/payment-methods", tags=["Payment Methods"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
# app.include_router(websocket.router, prefix="/api/ws", tags=["WebSocket"])