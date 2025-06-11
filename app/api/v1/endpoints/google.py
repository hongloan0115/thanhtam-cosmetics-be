from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import user as user_model
from app.schemas import user as user_schema
import requests
from app.core.config import settings
from app.core.logger import get_logger
from app.core.security import create_access_token
from fastapi.responses import RedirectResponse
from app.core.config import settings
from app.models.role import Role
from typing import Optional

GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI = settings.GOOGLE_REDIRECT_URI

logger = get_logger(__name__)

router = APIRouter()

@router.get("/login")
def google_login():
    # Redirect user to Google's OAuth 2.0 server
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?response_type=code"
        f"&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        "&scope=openid%20email%20profile"
        "&access_type=offline"
        "&prompt=consent"
    )
    logger.info("Redirecting user to Google OAuth login")
    return {"auth_url": google_auth_url}    

@router.get("/callback")
def google_callback(
    code: Optional[str] = None,
    error: Optional[str] = None,
    db: Session = Depends(get_db),
    request: Request = None
):
    logger.info("Received Google OAuth callback")
    # frontend_url = settings.FRONTEND_LOGIN_URL

    # Google OAuth authorization URL (Account Chooser)
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?response_type=code"
        f"&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        "&scope=openid%20email%20profile"
        "&access_type=offline"
        "&prompt=consent"
    )

    if error:
        logger.warning(f"Google OAuth error: {error}")
        raise HTTPException(status_code=400, detail="Google OAuth error")

    if not code:
        logger.error("Missing code in Google OAuth callback")
        raise HTTPException(status_code=400, detail="Missing code in Google OAuth callback")

    # Exchange code for access token
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    try:
        token_resp = requests.post(token_url, data=token_data)
    except Exception as e:
        logger.error(f"Error requesting token from Google: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error when contacting Google")
    if not token_resp.ok:
        logger.error(f"Failed to get token from Google: {token_resp.text}")
        raise HTTPException(status_code=400, detail="Failed to get token from Google")
    token_json = token_resp.json()
    access_token = token_json.get("access_token")
    id_token = token_json.get("id_token")

    # Get user info from Google
    try:
        userinfo_resp = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
    except Exception as e:
        logger.error(f"Error requesting user info from Google: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error when contacting Google")
    if not userinfo_resp.ok:
        logger.error(f"Failed to get user info from Google: {userinfo_resp.text}")
        raise HTTPException(status_code=400, detail="Failed to get user info from Google")
    userinfo = userinfo_resp.json()
    email = userinfo.get("email")
    name = userinfo.get("name")
    picture = userinfo.get("picture")

    # Check if user exists
    user = db.query(user_model.User).filter(user_model.User.email == email).first()
    if not user:
        logger.info(f"Creating new user for email: {email}")
        # Lấy vai trò KHACHHANG
        role = db.query(Role).filter(Role.tenVaiTro == "KHACHHANG").first()
        if not role:
            logger.error("Vai trò KHACHHANG chưa được cấu hình.")
            raise HTTPException(status_code=500, detail="Vai trò KHACHHANG chưa được cấu hình.")
        # Create new user
        new_user = user_model.User(
            tenNguoiDung=email.split("@")[0],
            hoTen=name,
            email=email,
            daXacThucEmail=True,
            anhDaiDien=picture,
            matKhauMaHoa="",  # No password for Google users
            trangThai=True
        )
        new_user.vaiTro.append(role)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        user = new_user
        logger.info(f"User created: {user.email}")
    else:
        logger.info(f"User exists: {user.email}")

    # Lấy danh sách vai trò của user (nếu có)
    roles = []
    if hasattr(user, "vaiTro"):
        roles = [role.tenVaiTro for role in getattr(user, "vaiTro", [])]

    # Tạo JWT token cho user
    access_token = create_access_token(data={"sub": user.email, "roles": roles})

    logger.info(f"Google sign up/login successful for: {user.email}")
    logger.info(f"Access token: {access_token}")

    # Redirect to frontend with accessToken as query param
    frontend_url = settings.FRONTEND_LOGIN_URL
    redirect_url = f"{frontend_url}?accessToken={access_token}"
    return RedirectResponse(url=redirect_url)
