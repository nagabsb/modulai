from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone, timedelta
import uuid

from database import db
from auth import hash_password, verify_password, create_jwt_token, get_current_user
from models import UserRegister, UserLogin, ForgotPasswordRequest, ResetPasswordRequest
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth")


@router.post("/register")
async def register(data: UserRegister):
    existing = await db.users.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "email": data.email,
        "password_hash": hash_password(data.password),
        "name": data.name,
        "role": "user",
        "token_balance": 5,
        "phone": data.phone,
        "school_name": data.school_name,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "last_login": None
    }

    await db.users.insert_one(user)
    token = create_jwt_token(user_id, data.email, "user")

    return {
        "token": token,
        "user": {
            "id": user_id,
            "email": data.email,
            "name": data.name,
            "role": "user",
            "token_balance": 5
        }
    }


@router.post("/login")
async def login(data: UserLogin):
    user = await db.users.find_one({"email": data.email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Email atau password salah")

    if not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Email atau password salah")

    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Akun Anda telah dinonaktifkan")

    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"last_login": datetime.now(timezone.utc).isoformat()}}
    )

    token = create_jwt_token(user["id"], user["email"], user["role"])

    return {
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "token_balance": user["token_balance"]
        }
    }


@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "token_balance": user["token_balance"],
        "phone": user.get("phone"),
        "school_name": user.get("school_name"),
        "created_at": user["created_at"]
    }


@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest):
    user = await db.users.find_one({"email": data.email})
    if not user:
        return {"message": "Jika email terdaftar, link reset password telah dikirim"}

    reset_token = str(uuid.uuid4())
    await db.password_resets.insert_one({
        "user_id": user["id"],
        "token": reset_token,
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
        "used": False
    })

    logger.info(f"Password reset token for {data.email}: {reset_token}")

    return {"message": "Jika email terdaftar, link reset password telah dikirim"}


@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest):
    reset = await db.password_resets.find_one({
        "token": data.token,
        "used": False
    })

    if not reset:
        raise HTTPException(status_code=400, detail="Token tidak valid atau sudah digunakan")

    if datetime.fromisoformat(reset["expires_at"]) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Token sudah kadaluarsa")

    await db.users.update_one(
        {"id": reset["user_id"]},
        {"$set": {"password_hash": hash_password(data.new_password)}}
    )

    await db.password_resets.update_one(
        {"token": data.token},
        {"$set": {"used": True}}
    )

    return {"message": "Password berhasil direset"}
