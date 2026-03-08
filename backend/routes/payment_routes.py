from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File
from fastapi.responses import FileResponse
from datetime import datetime, timezone
import uuid
import os
import logging
import midtransclient

from database import db
from config import TOKEN_PACKAGES, MIDTRANS_SERVER_KEY, MIDTRANS_IS_PRODUCTION
from auth import get_current_user
from models import PaymentRequest, VoucherApply

logger = logging.getLogger(__name__)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Bank transfer config
BANK_ACCOUNTS = [
    {
        "bank": "BCA",
        "account_number": "2470230889",
        "account_name": "NAJMI ABUBAKAR BASUMBUL"
    }
]

router = APIRouter(prefix="/api")

snap = midtransclient.Snap(
    is_production=MIDTRANS_IS_PRODUCTION,
    server_key=MIDTRANS_SERVER_KEY
)


@router.post("/payment/create")
async def create_payment(data: PaymentRequest, user: dict = Depends(get_current_user)):
    package = next((p for p in TOKEN_PACKAGES if p["id"] == data.package_id), None)
    if not package:
        raise HTTPException(status_code=404, detail="Paket tidak ditemukan")

    gross_amount = package["price"]
    discount = 0

    if data.voucher_code:
        voucher = await db.vouchers.find_one({
            "code": data.voucher_code.upper(),
            "is_active": True,
            "$or": [
                {"expires_at": {"$exists": False}},
                {"expires_at": {"$gt": datetime.now(timezone.utc).isoformat()}}
            ]
        })
        if voucher:
            if voucher.get("discount_type") == "percentage":
                discount = int(gross_amount * voucher["discount_value"] / 100)
            else:
                discount = voucher["discount_value"]
            gross_amount = max(gross_amount - discount, 0)

    order_id = f"MODULAI-{user['id'][:8]}-{int(datetime.now().timestamp())}"

    param = {
        "transaction_details": {
            "order_id": order_id,
            "gross_amount": gross_amount
        },
        "item_details": [{
            "id": package["id"],
            "price": gross_amount,
            "quantity": 1,
            "name": f"Paket {package['name']} ({package['tokens']} token)"
        }],
        "customer_details": {
            "first_name": data.name,
            "email": data.email,
            "phone": data.phone
        }
    }

    try:
        transaction = snap.create_transaction(param)

        await db.transactions.insert_one({
            "id": str(uuid.uuid4()),
            "user_id": user["id"],
            "order_id": order_id,
            "package_id": package["id"],
            "gross_amount": gross_amount,
            "original_amount": package["price"],
            "discount": discount,
            "voucher_code": data.voucher_code,
            "tokens_to_add": package["tokens"],
            "status": "pending",
            "payment_type": None,
            "snap_token": transaction["token"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        })

        return {
            "token": transaction["token"],
            "redirect_url": transaction.get("redirect_url"),
            "order_id": order_id
        }
    except Exception as e:
        logger.error(f"Midtrans error: {e}")
        raise HTTPException(status_code=500, detail=f"Gagal membuat pembayaran: {str(e)}")


@router.post("/payment/webhook")
async def payment_webhook(request: Request):
    body = await request.json()
    order_id = body.get("order_id")
    transaction_status = body.get("transaction_status")
    payment_type = body.get("payment_type")

    logger.info(f"Webhook received: {order_id} - {transaction_status}")

    transaction = await db.transactions.find_one({"order_id": order_id})
    if not transaction:
        logger.warning(f"Transaction not found: {order_id}")
        return {"status": "ok"}

    new_status = "pending"
    if transaction_status in ["capture", "settlement"]:
        new_status = "success"
        await db.users.update_one(
            {"id": transaction["user_id"]},
            {"$inc": {"token_balance": transaction["tokens_to_add"]}}
        )
        logger.info(f"Added {transaction['tokens_to_add']} tokens to user {transaction['user_id']}")
    elif transaction_status in ["deny", "expire", "cancel"]:
        new_status = "failed"

    await db.transactions.update_one(
        {"order_id": order_id},
        {"$set": {
            "status": new_status,
            "payment_type": payment_type,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )

    return {"status": "ok"}


@router.post("/voucher/apply")
async def apply_voucher(data: VoucherApply, user: dict = Depends(get_current_user)):
    voucher = await db.vouchers.find_one({
        "code": data.code.upper(),
        "is_active": True
    })

    if not voucher:
        raise HTTPException(status_code=404, detail="Kode voucher tidak valid")

    if voucher.get("expires_at") and voucher["expires_at"] < datetime.now(timezone.utc).isoformat():
        raise HTTPException(status_code=400, detail="Voucher sudah kadaluarsa")

    package = next((p for p in TOKEN_PACKAGES if p["id"] == data.package_id), None)
    if not package:
        raise HTTPException(status_code=404, detail="Paket tidak ditemukan")

    if voucher.get("discount_type") == "percentage":
        discount = int(package["price"] * voucher["discount_value"] / 100)
    else:
        discount = voucher["discount_value"]

    final_price = max(package["price"] - discount, 0)

    return {
        "valid": True,
        "discount": discount,
        "final_price": final_price,
        "message": f"Voucher valid! Diskon Rp {discount:,}"
    }


@router.get("/transactions")
async def get_user_transactions(user: dict = Depends(get_current_user)):
    transactions = await db.transactions.find(
        {"user_id": user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    return transactions



@router.get("/payment/bank-accounts")
async def get_bank_accounts():
    return BANK_ACCOUNTS


@router.post("/payment/bank-transfer")
async def create_bank_transfer(data: PaymentRequest, user: dict = Depends(get_current_user)):
    package = next((p for p in TOKEN_PACKAGES if p["id"] == data.package_id), None)
    if not package:
        raise HTTPException(status_code=404, detail="Paket tidak ditemukan")

    gross_amount = package["price"]
    discount = 0

    if data.voucher_code:
        voucher = await db.vouchers.find_one({
            "code": data.voucher_code.upper(),
            "is_active": True
        })
        if voucher:
            if voucher.get("discount_type") == "percentage":
                discount = int(gross_amount * voucher["discount_value"] / 100)
            else:
                discount = voucher["discount_value"]
            gross_amount = max(gross_amount - discount, 0)

    order_id = f"BT-{user['id'][:8]}-{int(datetime.now().timestamp())}"

    # Add unique code (3 random digits) to make amount unique for easier verification
    import random
    unique_code = random.randint(1, 999)
    final_amount = gross_amount + unique_code

    transaction = {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "order_id": order_id,
        "package_id": package["id"],
        "gross_amount": final_amount,
        "original_amount": package["price"],
        "discount": discount,
        "unique_code": unique_code,
        "voucher_code": data.voucher_code,
        "tokens_to_add": package["tokens"],
        "status": "pending",
        "payment_type": "bank_transfer",
        "proof_of_payment": None,
        "bank_account": BANK_ACCOUNTS[0],
        "customer_name": data.name,
        "customer_email": data.email,
        "customer_phone": data.phone,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    await db.transactions.insert_one(transaction)

    return {
        "order_id": order_id,
        "amount": final_amount,
        "unique_code": unique_code,
        "bank_account": BANK_ACCOUNTS[0],
        "package": package
    }


@router.get("/payment/bank-transfer/{order_id}")
async def get_bank_transfer_status(order_id: str, user: dict = Depends(get_current_user)):
    transaction = await db.transactions.find_one(
        {"order_id": order_id, "user_id": user["id"]},
        {"_id": 0}
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")
    return transaction


@router.post("/payment/upload-proof/{order_id}")
async def upload_proof_of_payment(order_id: str, file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    transaction = await db.transactions.find_one({
        "order_id": order_id,
        "user_id": user["id"],
        "payment_type": "bank_transfer"
    })
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")

    if transaction["status"] == "success":
        raise HTTPException(status_code=400, detail="Transaksi sudah dikonfirmasi")

    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="File harus berupa gambar (JPG, PNG, WebP)")

    # Save file
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{order_id}_{int(datetime.now().timestamp())}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    content = await file.read()
    if len(content) > 5 * 1024 * 1024:  # 5MB limit
        raise HTTPException(status_code=400, detail="Ukuran file maksimal 5MB")

    with open(filepath, "wb") as f:
        f.write(content)

    # Update transaction
    await db.transactions.update_one(
        {"order_id": order_id},
        {"$set": {
            "proof_of_payment": filename,
            "status": "waiting_verification",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )

    return {"message": "Bukti pembayaran berhasil diupload", "filename": filename}


@router.get("/uploads/{filename}")
async def serve_upload(filename: str):
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(filepath)
