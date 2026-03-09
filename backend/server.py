from fastapi import FastAPI
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from database import db
from config import SUPER_ADMIN_EMAIL, SUPER_ADMIN_PASSWORD, GEMINI_API_KEY
from auth import hash_password
from routes.auth_routes import router as auth_router
from routes.generate_routes import router as generate_router
from routes.payment_routes import router as payment_router
from routes.admin_routes import router as admin_router
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ModulAI API")

# Health check routes
@app.get("/api/")
async def root():
    return {"message": "ModulAI API is running", "version": "1.0.0"}

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

# Include all routers
app.include_router(auth_router)
app.include_router(generate_router)
app.include_router(payment_router)
app.include_router(admin_router)


@app.on_event("startup")
async def startup():
    admin = await db.users.find_one({"email": SUPER_ADMIN_EMAIL})
    if not admin:
        admin_user = {
            "id": str(uuid.uuid4()),
            "email": SUPER_ADMIN_EMAIL,
            "password_hash": hash_password(SUPER_ADMIN_PASSWORD),
            "name": "Super Admin",
            "role": "super_admin",
            "token_balance": 9999,
            "phone": None,
            "school_name": None,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(admin_user)
        logger.info(f"Created super admin: {SUPER_ADMIN_EMAIL}")

    voucher = await db.vouchers.find_one({"code": "GURU2024"})
    if not voucher:
        await db.vouchers.insert_one({
            "id": str(uuid.uuid4()),
            "code": "GURU2024",
            "discount_type": "percentage",
            "discount_value": 20,
            "is_active": True,
            "expires_at": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        logger.info("Created sample voucher: GURU2024")

    ai_settings = await db.settings.find_one({"key": "ai_settings"})
    if not ai_settings:
        await db.settings.insert_one({
            "key": "ai_settings",
            "value": {
                "provider": "gemini",
                "model": "gemini-2.5-flash"
            }
        })
        logger.info("Initialized AI settings")

    # Migrate: if no ai_keys exist but GEMINI_API_KEY is set, create default key
    existing_keys = await db.ai_keys.count_documents({})
    if existing_keys == 0 and GEMINI_API_KEY:
        import uuid as _uuid
        await db.ai_keys.insert_one({
            "id": str(_uuid.uuid4()),
            "provider": "gemini",
            "model": "gemini-2.5-flash",
            "api_key": GEMINI_API_KEY,
            "label": "Gemini Flash (Default)",
            "priority": 1,
            "is_active": True,
            "usage_count": 0,
            "last_used": None,
            "last_error": None,
            "last_error_at": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        logger.info("Migrated default Gemini API key to ai_keys collection")


@app.on_event("shutdown")
async def shutdown():
    from database import client
    client.close()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)
