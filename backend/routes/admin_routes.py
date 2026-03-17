from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel
import uuid
import logging

from database import db
from config import GEMINI_API_KEY, AI_PROVIDERS
from auth import get_admin_user
from models import AdminUserUpdate, SettingsUpdate, VoucherUpdate

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


# --- AI Keys Management ---

class AIKeyCreate(BaseModel):
    provider: str
    model: str
    api_key: str
    label: Optional[str] = None


class AIKeyUpdate(BaseModel):
    is_active: Optional[bool] = None
    priority: Optional[int] = None
    label: Optional[str] = None


@router.get("/ai-keys")
async def admin_get_ai_keys(admin: dict = Depends(get_admin_user)):
    keys = await db.ai_keys.find({}, {"_id": 0}).sort("priority", 1).to_list(100)
    # Mask API keys
    for k in keys:
        raw = k.get("api_key", "")
        k["api_key_masked"] = f"{raw[:8]}...{raw[-4:]}" if len(raw) > 12 else "***"
        del k["api_key"]
    return keys


@router.post("/ai-keys")
async def admin_create_ai_key(data: AIKeyCreate, admin: dict = Depends(get_admin_user)):
    # Validate provider and model
    if data.provider not in AI_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Provider tidak dikenal: {data.provider}")
    if data.model not in AI_PROVIDERS[data.provider]["models"]:
        raise HTTPException(status_code=400, detail=f"Model tidak valid untuk {data.provider}: {data.model}")

    # Get next priority
    max_priority = await db.ai_keys.find_one(sort=[("priority", -1)])
    next_priority = (max_priority.get("priority", 0) + 1) if max_priority else 1

    model_info = AI_PROVIDERS[data.provider]["models"][data.model]
    key_doc = {
        "id": str(uuid.uuid4()),
        "provider": data.provider,
        "model": data.model,
        "api_key": data.api_key,
        "label": data.label or f"{model_info['name']} Key {next_priority}",
        "priority": next_priority,
        "is_active": True,
        "usage_count": 0,
        "last_used": None,
        "last_error": None,
        "last_error_at": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.ai_keys.insert_one(key_doc)
    key_doc.pop("_id", None)
    key_doc["api_key_masked"] = f"{data.api_key[:8]}...{data.api_key[-4:]}" if len(data.api_key) > 12 else "***"
    del key_doc["api_key"]
    return key_doc


class AIKeyReorder(BaseModel):
    key_ids: List[str]


@router.put("/ai-keys/reorder")
async def admin_reorder_ai_keys(data: AIKeyReorder, admin: dict = Depends(get_admin_user)):
    for i, key_id in enumerate(data.key_ids):
        await db.ai_keys.update_one({"id": key_id}, {"$set": {"priority": i + 1}})
    return {"message": "Urutan key berhasil diubah"}


@router.put("/ai-keys/{key_id}")
async def admin_update_ai_key(key_id: str, data: AIKeyUpdate, admin: dict = Depends(get_admin_user)):
    update_data = {}
    if data.is_active is not None:
        update_data["is_active"] = data.is_active
    if data.priority is not None:
        update_data["priority"] = data.priority
    if data.label is not None:
        update_data["label"] = data.label

    if not update_data:
        raise HTTPException(status_code=400, detail="Tidak ada data untuk diupdate")

    result = await db.ai_keys.update_one({"id": key_id}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Key tidak ditemukan")
    return {"message": "Key berhasil diupdate"}


@router.delete("/ai-keys/{key_id}")
async def admin_delete_ai_key(key_id: str, admin: dict = Depends(get_admin_user)):
    result = await db.ai_keys.delete_one({"id": key_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Key tidak ditemukan")
    return {"message": "Key berhasil dihapus"}


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


# --- Delete endpoints for Users, Generations, Transactions ---

@router.delete("/users/{user_id}")
async def admin_delete_user(user_id: str, admin: dict = Depends(get_admin_user)):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    if user.get("role") == "super_admin":
        raise HTTPException(status_code=403, detail="Tidak bisa menghapus super admin")

    # Delete user and related data
    await db.generations.delete_many({"user_id": user_id})
    await db.transactions.delete_many({"user_id": user_id})
    await db.users.delete_one({"id": user_id})

    return {"message": "User dan semua data terkait berhasil dihapus"}


@router.delete("/generations/{generation_id}")
async def admin_delete_generation(generation_id: str, admin: dict = Depends(get_admin_user)):
    result = await db.generations.delete_one({"id": generation_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Generasi tidak ditemukan")
    return {"message": "Generasi berhasil dihapus"}


@router.delete("/generations")
async def admin_delete_all_generations(admin: dict = Depends(get_admin_user)):
    result = await db.generations.delete_many({})
    return {"message": f"{result.deleted_count} generasi berhasil dihapus"}


@router.delete("/transactions/{transaction_id}")
async def admin_delete_transaction(transaction_id: str, admin: dict = Depends(get_admin_user)):
    result = await db.transactions.delete_one({"id": transaction_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")
    return {"message": "Transaksi berhasil dihapus"}



@router.put("/transactions/{transaction_id}/verify")
async def admin_verify_transaction(transaction_id: str, admin: dict = Depends(get_admin_user)):
    transaction = await db.transactions.find_one({"id": transaction_id})
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")

    if transaction["status"] == "success":
        raise HTTPException(status_code=400, detail="Transaksi sudah dikonfirmasi sebelumnya")

    # Update transaction status
    await db.transactions.update_one(
        {"id": transaction_id},
        {"$set": {
            "status": "success",
            "verified_by": admin["id"],
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )

    # Add tokens to user
    await db.users.update_one(
        {"id": transaction["user_id"]},
        {"$inc": {"token_balance": transaction["tokens_to_add"]}}
    )

    logger.info(f"Admin verified transaction {transaction_id}, added {transaction['tokens_to_add']} tokens to user {transaction['user_id']}")

    return {"message": f"Transaksi dikonfirmasi. {transaction['tokens_to_add']} token ditambahkan ke akun user."}


@router.put("/transactions/{transaction_id}/reject")
async def admin_reject_transaction(transaction_id: str, admin: dict = Depends(get_admin_user)):
    transaction = await db.transactions.find_one({"id": transaction_id})
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")

    if transaction["status"] == "success":
        raise HTTPException(status_code=400, detail="Tidak bisa menolak transaksi yang sudah sukses")

    await db.transactions.update_one(
        {"id": transaction_id},
        {"$set": {
            "status": "rejected",
            "rejected_by": admin["id"],
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )

    return {"message": "Transaksi ditolak."}
