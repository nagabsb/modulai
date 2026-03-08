from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime, timezone
import uuid
import logging

from database import db
from config import GEMINI_API_KEY
from auth import get_admin_user
from models import AdminUserUpdate, SettingsUpdate, AISettingsUpdate, VoucherUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin")


@router.get("/dashboard")
async def admin_dashboard(admin: dict = Depends(get_admin_user)):
    total_users = await db.users.count_documents({"role": "user"})
    total_revenue = 0
    successful_txs = await db.transactions.find({"status": "success"}).to_list(10000)
    for tx in successful_txs:
        total_revenue += tx.get("gross_amount", 0)

    total_generations = await db.generations.count_documents({})
    total_tokens_in_circulation = 0
    users_cursor = db.users.find({}, {"token_balance": 1})
    async for u in users_cursor:
        total_tokens_in_circulation += u.get("token_balance", 0)

    doc_types = ["modul", "rpp", "lkpd", "soal", "rubrik"]
    doc_breakdown = {}
    for dt in doc_types:
        count = await db.generations.count_documents({"doc_type": dt})
        doc_breakdown[dt] = count

    recent_txs = await db.transactions.find({}, {"_id": 0}).sort("created_at", -1).limit(10).to_list(10)

    return {
        "total_users": total_users,
        "total_revenue": total_revenue,
        "total_generations": total_generations,
        "total_tokens_circulation": total_tokens_in_circulation,
        "doc_breakdown": doc_breakdown,
        "recent_transactions": recent_txs
    }


@router.get("/users")
async def admin_get_users(admin: dict = Depends(get_admin_user), skip: int = 0, limit: int = 50):
    users = await db.users.find(
        {},
        {"_id": 0, "password_hash": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)

    total = await db.users.count_documents({})
    return {"users": users, "total": total}


@router.put("/users/{user_id}")
async def admin_update_user(user_id: str, data: AdminUserUpdate, admin: dict = Depends(get_admin_user)):
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}

    if data.token_balance is not None:
        update_data["token_balance"] = data.token_balance
    if data.is_active is not None:
        update_data["is_active"] = data.is_active

    result = await db.users.update_one({"id": user_id}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")

    return {"message": "User berhasil diupdate"}


@router.get("/transactions")
async def admin_get_transactions(admin: dict = Depends(get_admin_user), status: Optional[str] = None, skip: int = 0, limit: int = 50):
    query = {}
    if status:
        query["status"] = status

    transactions = await db.transactions.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.transactions.count_documents(query)

    return {"transactions": transactions, "total": total}


@router.get("/generations")
async def admin_get_generations(admin: dict = Depends(get_admin_user), skip: int = 0, limit: int = 50):
    pipeline = [
        {"$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "id",
            "as": "user"
        }},
        {"$unwind": {"path": "$user", "preserveNullAndEmptyArrays": True}},
        {"$project": {
            "_id": 0,
            "id": 1,
            "doc_type": 1,
            "created_at": 1,
            "user_email": "$user.email",
            "user_name": "$user.name",
            "form_data.topik": 1,
            "form_data.mata_pelajaran": 1
        }},
        {"$sort": {"created_at": -1}},
        {"$skip": skip},
        {"$limit": limit}
    ]

    generations = await db.generations.aggregate(pipeline).to_list(limit)
    total = await db.generations.count_documents({})

    return {"generations": generations, "total": total}


@router.get("/settings")
async def admin_get_settings(admin: dict = Depends(get_admin_user)):
    settings = await db.settings.find({}, {"_id": 0}).to_list(100)
    return settings


@router.put("/settings")
async def admin_update_settings(data: SettingsUpdate, admin: dict = Depends(get_admin_user)):
    await db.settings.update_one(
        {"key": data.key},
        {"$set": {"key": data.key, "value": data.value}},
        upsert=True
    )
    return {"message": "Setting berhasil diupdate"}


@router.get("/ai-settings")
async def admin_get_ai_settings(admin: dict = Depends(get_admin_user)):
    from routes.generate_routes import get_ai_settings
    settings = await get_ai_settings()
    if settings.get("gemini_api_key"):
        key = settings["gemini_api_key"]
        settings["gemini_api_key_masked"] = f"{key[:10]}...{key[-4:]}" if len(key) > 14 else "***"
    return settings


@router.put("/ai-settings")
async def admin_update_ai_settings(data: AISettingsUpdate, admin: dict = Depends(get_admin_user)):
    from routes.generate_routes import get_ai_settings
    current = await get_ai_settings()

    update_value = {
        "provider": data.provider,
        "gemini_api_key": data.gemini_api_key if data.gemini_api_key else current.get("gemini_api_key", GEMINI_API_KEY)
    }

    if data.provider == "gemini_pro":
        update_value["model"] = "gemini-2.5-pro"
    else:
        update_value["model"] = "gemini-2.5-flash"

    await db.settings.update_one(
        {"key": "ai_settings"},
        {"$set": {"key": "ai_settings", "value": update_value}},
        upsert=True
    )
    return {"message": "AI settings berhasil diupdate"}


@router.post("/vouchers")
async def admin_create_voucher(admin: dict = Depends(get_admin_user), code: str = "", discount_type: str = "fixed", discount_value: int = 0, expires_at: Optional[str] = None):
    voucher = {
        "id": str(uuid.uuid4()),
        "code": code.upper(),
        "discount_type": discount_type,
        "discount_value": discount_value,
        "is_active": True,
        "expires_at": expires_at,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.vouchers.insert_one(voucher)
    voucher.pop("_id", None)
    return voucher


@router.get("/vouchers")
async def admin_get_vouchers(admin: dict = Depends(get_admin_user)):
    vouchers = await db.vouchers.find({}, {"_id": 0}).to_list(100)
    return vouchers


@router.put("/vouchers/{voucher_id}")
async def admin_update_voucher(voucher_id: str, data: VoucherUpdate, admin: dict = Depends(get_admin_user)):
    update_data = {}
    if data.is_active is not None:
        update_data["is_active"] = data.is_active

    if not update_data:
        raise HTTPException(status_code=400, detail="Tidak ada data untuk diupdate")

    result = await db.vouchers.update_one({"id": voucher_id}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Voucher tidak ditemukan")

    return {"message": "Voucher berhasil diupdate"}


@router.delete("/vouchers/{voucher_id}")
async def admin_delete_voucher(voucher_id: str, admin: dict = Depends(get_admin_user)):
    result = await db.vouchers.delete_one({"id": voucher_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Voucher tidak ditemukan")

    return {"message": "Voucher berhasil dihapus"}
