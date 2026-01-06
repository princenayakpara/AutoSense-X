from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db, User
from auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_active_user, send_otp_email, generate_otp,
    store_otp, verify_otp
)
from pydantic import BaseModel, EmailStr
import httpx, os, secrets
from datetime import datetime

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ---------- Models ----------

class OTPRequest(BaseModel):
    email: EmailStr

class OTPVerify(BaseModel):
    email: EmailStr
    otp: str
    username: str
    password: str

class MobileLogin(BaseModel):
    token: str


# ---------- Email + Password Login ----------

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.username})
    user.last_login = datetime.utcnow()
    db.commit()

    return {"access_token": token, "token_type": "bearer"}


# ---------- OTP Registration ----------

@router.post("/register/request")
async def request_otp(data: OTPRequest):
    otp = generate_otp()
    store_otp(data.email, otp)

    if not send_otp_email(data.email, otp):
        raise HTTPException(status_code=500, detail="Failed to send email")

    return {"success": True, "message": "OTP sent to email"}

@router.post("/register/verify")
async def verify_registration(data: OTPVerify, db: Session = Depends(get_db)):
    if not verify_otp(data.email, data.otp):
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if db.query(User).filter((User.email == data.email) | (User.username == data.username)).first():
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        email=data.email,
        username=data.username,
        hashed_password=get_password_hash(data.password),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


# ---------- Google OAuth ----------

@router.get("/google")
async def google_login(request: Request):
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    # Dynamic redirect URI based on request host
    host = str(request.base_url).rstrip('/')
    default_redirect = f"{host}/api/auth/google/callback"
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", default_redirect)

    if not client_id:
        raise HTTPException(status_code=500, detail="GOOGLE_CLIENT_ID not configured")

    state = secrets.token_urlsafe(16)
    google_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope=openid email profile"
        f"&state={state}"
    )

    return RedirectResponse(google_url)

@router.get("/google/callback")
async def google_callback(request: Request, code: str, db: Session = Depends(get_db)):
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    
    host = str(request.base_url).rstrip('/')
    default_redirect = f"{host}/api/auth/google/callback"
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", default_redirect)

    async with httpx.AsyncClient() as client:
        token_res = await client.post("https://oauth2.googleapis.com/token", data={
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        })

        token_data = token_res.json()
        access_token = token_data.get("access_token")

        user_res = await client.get("https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"})
        user_info = user_res.json()

    email = user_info["email"]
    google_id = user_info["id"]

    user = db.query(User).filter((User.email == email) | (User.google_id == google_id)).first()
    if not user:
        user = User(email=email, username=email.split("@")[0], google_id=google_id, is_active=True)
        db.add(user)

    user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(user)

    jwt_token = create_access_token({"sub": user.username})
    return RedirectResponse(f"{host}/?token={jwt_token}")


# ---------- Protected ----------

@router.get("/me")
async def get_me(user: User = Depends(get_current_active_user)):
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "is_admin": user.is_admin
    }


# ---------- Mobile ----------

@router.post("/mobile/login")
async def mobile_login(data: MobileLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.token).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
