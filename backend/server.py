from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
import midtransclient
import httpx
import json
import re

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Config
JWT_SECRET = os.environ.get('JWT_SECRET', 'default_secret')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 7

# Midtrans Config
MIDTRANS_SERVER_KEY = os.environ.get('MIDTRANS_SERVER_KEY')
MIDTRANS_CLIENT_KEY = os.environ.get('MIDTRANS_CLIENT_KEY')
MIDTRANS_IS_PRODUCTION = os.environ.get('MIDTRANS_IS_PRODUCTION', 'false').lower() == 'true'

# Gemini Config
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Super Admin Config
SUPER_ADMIN_EMAIL = os.environ.get('SUPER_ADMIN_EMAIL')
SUPER_ADMIN_PASSWORD = os.environ.get('SUPER_ADMIN_PASSWORD')

# Initialize Midtrans Snap
snap = midtransclient.Snap(
    is_production=MIDTRANS_IS_PRODUCTION,
    server_key=MIDTRANS_SERVER_KEY
)

app = FastAPI(title="ModulAI API")
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============== MODELS ==============

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: Optional[str] = None
    school_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    token_balance: int
    phone: Optional[str] = None
    school_name: Optional[str] = None
    created_at: str

class TokenPackage(BaseModel):
    id: str
    name: str
    price: int
    tokens: int
    documents_estimate: int

class GenerateRequest(BaseModel):
    doc_type: str  # modul, rpp, lkpd, soal, rubrik
    jenjang: str
    kelas: str
    kurikulum: str
    semester: str
    fase: str
    mata_pelajaran: str
    topik: str
    alokasi_waktu: int
    tingkat_kesulitan: Optional[str] = "Sedang"
    jumlah_pg: Optional[int] = 0
    jumlah_isian: Optional[int] = 0
    jumlah_essay: Optional[int] = 0
    sertakan_pembahasan: Optional[bool] = True
    # Custom physics values
    use_custom_values: Optional[bool] = False
    resistor1: Optional[float] = None
    resistor2: Optional[float] = None
    voltage: Optional[float] = None

class PaymentRequest(BaseModel):
    package_id: str
    name: str
    email: str
    phone: str
    voucher_code: Optional[str] = None

class VoucherApply(BaseModel):
    code: str
    package_id: str

class AdminUserUpdate(BaseModel):
    token_balance: Optional[int] = None
    is_active: Optional[bool] = None

class SettingsUpdate(BaseModel):
    key: str
    value: Any

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class AISettingsUpdate(BaseModel):
    provider: str  # gemini_flash_lite, gemini_pro
    gemini_api_key: Optional[str] = None

class MultiGenerateRequest(BaseModel):
    doc_types: List[str]  # ["modul", "rpp", "lkpd", "soal", "rubrik"]
    jenjang: str
    kelas: str
    kurikulum: str
    semester: str
    fase: str
    mata_pelajaran: str
    topik: str
    alokasi_waktu: int
    tingkat_kesulitan: Optional[str] = "Sedang"
    jumlah_pg: Optional[int] = 0
    jumlah_isian: Optional[int] = 0
    jumlah_essay: Optional[int] = 0
    sertakan_pembahasan: Optional[bool] = True
    use_custom_values: Optional[bool] = False
    resistor1: Optional[float] = None
    resistor2: Optional[float] = None
    voltage: Optional[float] = None

class VoucherUpdate(BaseModel):
    is_active: Optional[bool] = None

# ============== HELPERS ==============

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_jwt_token(user_id: str, email: str, role: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRATION_DAYS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_jwt_token(credentials.credentials)
    user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account suspended")
    return user

async def get_admin_user(user: dict = Depends(get_current_user)):
    if user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# Token Packages
TOKEN_PACKAGES = [
    {"id": "starter", "name": "Starter", "price": 99000, "tokens": 100, "documents_estimate": 40},
    {"id": "pro", "name": "Pro", "price": 249000, "tokens": 300, "documents_estimate": 120},
    {"id": "guru", "name": "Guru", "price": 399000, "tokens": 750, "documents_estimate": 300},
    {"id": "sekolah", "name": "Sekolah", "price": 899000, "tokens": 2000, "documents_estimate": 800},
]

# ============== AI GENERATION ==============

async def get_ai_settings():
    """Get AI settings from database or use defaults"""
    settings = await db.settings.find_one({"key": "ai_settings"})
    if settings:
        return settings["value"]
    return {
        "provider": "gemini_flash_lite",
        "gemini_api_key": GEMINI_API_KEY,
        "model": "gemini-2.5-flash"
    }

async def generate_with_gemini(prompt: str) -> str:
    """Generate content using Gemini API directly"""
    ai_settings = await get_ai_settings()
    api_key = ai_settings.get("gemini_api_key") or GEMINI_API_KEY
    
    # Model selection based on provider setting
    provider = ai_settings.get("provider", "gemini_flash_lite")
    if provider == "gemini_pro":
        model = "gemini-2.5-pro"
    else:
        model = "gemini-2.5-flash"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 8192,
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Extract text from response
            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    text = candidate["content"]["parts"][0].get("text", "")
                    return text
            
            raise HTTPException(status_code=500, detail="Empty response from AI")
    except httpx.HTTPStatusError as e:
        logger.error(f"Gemini API error: {e.response.text}")
        raise HTTPException(status_code=500, detail=f"Gagal generate dokumen: {e.response.text}")
    except Exception as e:
        logger.error(f"Gemini generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Gagal generate dokumen: {str(e)}")

def build_prompt(data: GenerateRequest) -> str:
    """Build prompt based on document type"""
    base_info = f"""
Jenjang: {data.jenjang}
Kelas: {data.kelas}
Kurikulum: {data.kurikulum}
Semester: {data.semester}
Fase: {data.fase}
Mata Pelajaran: {data.mata_pelajaran}
Topik/Materi: {data.topik}
Alokasi Waktu: {data.alokasi_waktu} menit
"""
    
    # Physics diagram instructions
    physics_diagram_instruction = ""
    if data.mata_pelajaran.lower() in ["fisika", "ipa"] and data.doc_type == "soal":
        custom_values = ""
        if data.use_custom_values and data.resistor1 and data.voltage:
            custom_values = f"""
NILAI CUSTOM YANG HARUS DIGUNAKAN:
- Resistor 1: {data.resistor1} Ohm
- Resistor 2: {data.resistor2 or data.resistor1} Ohm
- Tegangan: {data.voltage} Volt
"""
        
        physics_diagram_instruction = f"""
INSTRUKSI KHUSUS UNTUK SOAL FISIKA:
{custom_values}

Untuk soal tentang RANGKAIAN LISTRIK, tambahkan tag berikut SEBELUM teks soal:
[DIAGRAM:circuit,type=series,R1=2,R2=3,V=12]
atau
[DIAGRAM:circuit,type=parallel,R1=4,R2=6,V=24]

Untuk soal tentang PENGUKURAN (ammeter/voltmeter), tambahkan tag:
[DIAGRAM:meter,type=ammeter,needle=70,range=0.5 A]
atau
[DIAGRAM:meter,type=voltmeter,needle=45,range=10 V]

Untuk soal tentang BIDANG MIRING, tambahkan tag:
[DIAGRAM:physics,scene=inclined-plane,angle=30,mass=5]

Untuk soal tentang GERAK PARABOLA, tambahkan tag:
[DIAGRAM:physics,scene=projectile,angle=45,v0=20]

Untuk soal tentang KATROL, tambahkan tag:
[DIAGRAM:physics,scene=pulley,m1=5,m2=3]

Tag diagram WAJIB ada untuk setiap soal yang relevan dengan topik di atas.
"""
    
    if data.doc_type == "modul":
        return f"""Buatkan Modul Ajar lengkap dengan format berikut:
{base_info}

Struktur Modul Ajar:
1. INFORMASI UMUM
   - Identitas Modul
   - Kompetensi Awal
   - Profil Pelajar Pancasila
   - Sarana Prasarana
   - Target Peserta Didik
   - Model Pembelajaran

2. KOMPONEN INTI
   - Capaian Pembelajaran (CP)
   - Tujuan Pembelajaran (TP)
   - Alur Tujuan Pembelajaran (ATP)
   - Pemahaman Bermakna
   - Pertanyaan Pemantik
   - Kegiatan Pembelajaran (Pendahuluan, Inti, Penutup)
   - Asesmen (Diagnostik, Formatif, Sumatif)
   - Pengayaan dan Remedial

3. LAMPIRAN
   - Lembar Kerja Peserta Didik
   - Bahan Bacaan
   - Glosarium

4. DAFTAR PUSTAKA
   Wajib sertakan referensi resmi berikut (sesuaikan dengan mata pelajaran dan jenjang):
   - Kementerian Pendidikan, Kebudayaan, Riset, dan Teknologi. (2024). Panduan Pembelajaran dan Asesmen Kurikulum Merdeka. Jakarta: Kemendikbudristek. Tersedia di: kurikulum.kemendikdasmen.go.id
   - Badan Standar, Kurikulum, dan Asesmen Pendidikan. (2022). Capaian Pembelajaran {data.mata_pelajaran} Fase {data.fase}. Jakarta: BSKAP.
   - Pusat Perbukuan. (2024). Buku Panduan Guru {data.mata_pelajaran} Kelas {data.kelas} {data.jenjang}. Jakarta: Kemendikdasmen. Tersedia di: buku.kemendikdasmen.go.id
   - Tambahkan 2-3 sumber relevan lainnya (buku teks, jurnal pendidikan, atau sumber resmi pemerintah)

Format output: HTML dengan tabel berformat (header #1E3A5F, teks putih). Gunakan LaTeX untuk rumus matematika ($formula$ untuk inline, $$formula$$ untuk block). JANGAN gunakan emoji."""

    elif data.doc_type == "rpp":
        return f"""Buatkan RPP (Rencana Pelaksanaan Pembelajaran) dengan format:
{base_info}

Struktur RPP:
1. Identitas RPP
2. Kompetensi Inti (KI) / Capaian Pembelajaran (CP)
3. Kompetensi Dasar (KD) / Tujuan Pembelajaran (TP)
4. Indikator Pencapaian Kompetensi
5. Materi Pembelajaran
6. Metode Pembelajaran
7. Kegiatan Pembelajaran:
   - Pendahuluan ({int(data.alokasi_waktu * 0.15)} menit)
   - Inti ({int(data.alokasi_waktu * 0.7)} menit)
   - Penutup ({int(data.alokasi_waktu * 0.15)} menit)
8. Penilaian
9. Sumber dan Media Pembelajaran

Format output: HTML dengan tabel berformat (header #1E3A5F, teks putih). JANGAN gunakan emoji."""

    elif data.doc_type == "lkpd":
        return f"""Buatkan LKPD (Lembar Kerja Peserta Didik) dengan format:
{base_info}

Struktur LKPD:
1. Judul LKPD
2. Identitas Siswa (nama, kelas, tanggal)
3. Petunjuk Pengerjaan
4. Kompetensi yang Dicapai
5. Ringkasan Materi (singkat)
6. Kegiatan 1: [Aktivitas eksplorasi]
7. Kegiatan 2: [Aktivitas diskusi/praktik]
8. Kegiatan 3: [Aktivitas penerapan]
9. Kesimpulan (isian untuk siswa)
10. Refleksi Diri

Buat dengan desain menarik, ada kotak isian untuk jawaban siswa (gunakan <u>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</u> untuk garis isian). Format: HTML dengan tabel. JANGAN gunakan emoji."""

    elif data.doc_type == "soal":
        difficulty_map = {
            "Mudah": "C1-C2 (Mengingat, Memahami)",
            "Sedang": "C3-C4 (Menerapkan, Menganalisis)",
            "Sulit": "C5-C6 (Mengevaluasi, Mencipta)",
            "Campuran": "C1-C6 (bervariasi)"
        }
        
        pembahasan_instruction = """

════════════════════════════════════════════════════════════════

PEMBAHASAN

(Untuk setiap soal, berikan penjelasan detail dengan rumus dan langkah penyelesaian)
1. [Pembahasan lengkap soal 1]
2. [Pembahasan lengkap soal 2]
... dst""" if data.sertakan_pembahasan else ""
        
        return f"""Buatkan Bank Soal dengan spesifikasi:
{base_info}
Tingkat Kesulitan: {data.tingkat_kesulitan} - {difficulty_map.get(data.tingkat_kesulitan, '')}

{physics_diagram_instruction}

Jumlah Soal:
- Pilihan Ganda (PG): {data.jumlah_pg} soal
- Isian Singkat: {data.jumlah_isian} soal
- Essay/Uraian: {data.jumlah_essay} soal

PENTING - FORMAT OUTPUT HARUS SEPERTI INI:

════════════════════════════════════════════════════════════════
BANK SOAL {data.mata_pelajaran.upper()}
Kelas {data.kelas} {data.jenjang} | {data.kurikulum} | Semester {data.semester}
════════════════════════════════════════════════════════════════

I. SOAL PILIHAN GANDA

1. [Soal pertama dengan rumus LaTeX jika perlu]
   A. [Pilihan jawaban]
   B. [Pilihan jawaban]
   C. [Pilihan jawaban]
   D. [Pilihan jawaban]
   E. [Pilihan jawaban]

2. [Soal kedua]
   A. ...
   B. ...
   C. ...
   D. ...
   E. ...

(Lanjutkan sampai {data.jumlah_pg} soal PG selesai)

════════════════════════════════════════════════════════════════

II. SOAL ISIAN SINGKAT

1. [Soal isian] _______________
2. [Soal isian] _______________
(Lanjutkan sampai {data.jumlah_isian} soal isian selesai)

════════════════════════════════════════════════════════════════

III. SOAL ESSAY/URAIAN

1. [Soal essay lengkap]
2. [Soal essay lengkap]
(Lanjutkan sampai {data.jumlah_essay} soal essay selesai)

════════════════════════════════════════════════════════════════
════════════════════════════════════════════════════════════════

KUNCI JAWABAN

I. Pilihan Ganda
1. [Huruf]    6. [Huruf]    11. [Huruf]
2. [Huruf]    7. [Huruf]    12. [Huruf]
3. [Huruf]    8. [Huruf]    13. [Huruf]
4. [Huruf]    9. [Huruf]    14. [Huruf]
5. [Huruf]   10. [Huruf]    15. [Huruf]
(Sesuaikan dengan jumlah soal)

II. Isian Singkat
1. [Jawaban]
2. [Jawaban]
... dst

III. Essay
1. [Jawaban lengkap]
2. [Jawaban lengkap]
... dst
{pembahasan_instruction}

════════════════════════════════════════════════════════════════

CATATAN PENTING:
- SEMUA SOAL harus ditulis LENGKAP terlebih dahulu
- KUNCI JAWABAN ditulis SETELAH semua soal selesai
- PEMBAHASAN (jika ada) ditulis PALING AKHIR setelah kunci jawaban
- Untuk Matematika/Fisika, gunakan LaTeX: $formula$ untuk inline atau $$formula$$ untuk display
- Format output: HTML dengan pemisah yang jelas. JANGAN gunakan emoji."""

    elif data.doc_type == "rubrik":
        return f"""Buatkan Rubrik Asesmen dengan format:
{base_info}

Struktur Rubrik:
1. Judul Asesmen
2. Tujuan Asesmen
3. Kriteria Penilaian
4. Tabel Rubrik dengan:
   - Aspek yang Dinilai
   - Kriteria per Level (4 = Sangat Baik, 3 = Baik, 2 = Cukup, 1 = Kurang)
   - Deskripsi per Level
   - Bobot/Skor
5. Cara Penggunaan Rubrik
6. Contoh Penghitungan Nilai

Format: HTML dengan tabel rubrik yang jelas. Header tabel: background #1E3A5F, teks putih. JANGAN gunakan emoji."""

    return f"Buatkan dokumen pendidikan tentang: {data.topik}"

# ============== AUTH ROUTES ==============

@api_router.post("/auth/register")
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
        "token_balance": 5,  # Free starter tokens
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

@api_router.post("/auth/login")
async def login(data: UserLogin):
    user = await db.users.find_one({"email": data.email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Email atau password salah")
    
    if not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Email atau password salah")
    
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Akun Anda telah dinonaktifkan")
    
    # Update last login
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

@api_router.get("/auth/me")
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

@api_router.post("/auth/forgot-password")
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

@api_router.post("/auth/reset-password")
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

# ============== TOKEN PACKAGES ==============

@api_router.get("/packages")
async def get_packages():
    settings = await db.settings.find_one({"key": "token_packages"})
    if settings:
        return settings["value"]
    return TOKEN_PACKAGES

# ============== DOCUMENT GENERATION ==============

@api_router.post("/generate")
async def generate_document(data: GenerateRequest, user: dict = Depends(get_current_user)):
    # Check token balance
    if user["token_balance"] < 1:
        raise HTTPException(status_code=402, detail="Token tidak mencukupi. Silakan top up.")
    
    # Build and send prompt
    prompt = build_prompt(data)
    result_html = await generate_with_gemini(prompt)
    
    # Clean up result - remove markdown code blocks if present
    result_html = re.sub(r'^```html?\n?', '', result_html)
    result_html = re.sub(r'\n?```$', '', result_html)
    
    # Save generation record
    generation_id = str(uuid.uuid4())
    generation = {
        "id": generation_id,
        "user_id": user["id"],
        "doc_type": data.doc_type,
        "form_data": data.model_dump(),
        "result_html": result_html,
        "tokens_used": 1,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.generations.insert_one(generation)
    
    # Deduct token
    await db.users.update_one(
        {"id": user["id"]},
        {"$inc": {"token_balance": -1}}
    )
    
    return {
        "id": generation_id,
        "result_html": result_html,
        "tokens_used": 1,
        "remaining_tokens": user["token_balance"] - 1
    }

@api_router.get("/generations")
async def get_generations(user: dict = Depends(get_current_user), skip: int = 0, limit: int = 20):
    generations = await db.generations.find(
        {"user_id": user["id"]},
        {"_id": 0, "result_html": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    total = await db.generations.count_documents({"user_id": user["id"]})
    
    return {"generations": generations, "total": total}

@api_router.get("/generations/{generation_id}")
async def get_generation(generation_id: str, user: dict = Depends(get_current_user)):
    generation = await db.generations.find_one(
        {"id": generation_id, "user_id": user["id"]},
        {"_id": 0}
    )
    if not generation:
        raise HTTPException(status_code=404, detail="Dokumen tidak ditemukan")
    return generation

# ============== PAYMENT ROUTES ==============

@api_router.post("/payment/create")
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

@api_router.post("/payment/webhook")
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

@api_router.post("/voucher/apply")
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

@api_router.get("/transactions")
async def get_user_transactions(user: dict = Depends(get_current_user)):
    transactions = await db.transactions.find(
        {"user_id": user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    return transactions

# ============== ADMIN ROUTES ==============

@api_router.get("/admin/dashboard")
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

@api_router.get("/admin/users")
async def admin_get_users(admin: dict = Depends(get_admin_user), skip: int = 0, limit: int = 50):
    users = await db.users.find(
        {},
        {"_id": 0, "password_hash": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    total = await db.users.count_documents({})
    return {"users": users, "total": total}

@api_router.put("/admin/users/{user_id}")
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

@api_router.get("/admin/transactions")
async def admin_get_transactions(admin: dict = Depends(get_admin_user), status: Optional[str] = None, skip: int = 0, limit: int = 50):
    query = {}
    if status:
        query["status"] = status
    
    transactions = await db.transactions.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.transactions.count_documents(query)
    
    return {"transactions": transactions, "total": total}

@api_router.get("/admin/generations")
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

@api_router.get("/admin/settings")
async def admin_get_settings(admin: dict = Depends(get_admin_user)):
    settings = await db.settings.find({}, {"_id": 0}).to_list(100)
    return settings

@api_router.put("/admin/settings")
async def admin_update_settings(data: SettingsUpdate, admin: dict = Depends(get_admin_user)):
    await db.settings.update_one(
        {"key": data.key},
        {"$set": {"key": data.key, "value": data.value}},
        upsert=True
    )
    return {"message": "Setting berhasil diupdate"}

# AI Settings endpoints
@api_router.get("/admin/ai-settings")
async def admin_get_ai_settings(admin: dict = Depends(get_admin_user)):
    settings = await get_ai_settings()
    # Mask API key for security
    if settings.get("gemini_api_key"):
        key = settings["gemini_api_key"]
        settings["gemini_api_key_masked"] = f"{key[:10]}...{key[-4:]}" if len(key) > 14 else "***"
    return settings

@api_router.put("/admin/ai-settings")
async def admin_update_ai_settings(data: AISettingsUpdate, admin: dict = Depends(get_admin_user)):
    current = await get_ai_settings()
    
    update_value = {
        "provider": data.provider,
        "gemini_api_key": data.gemini_api_key if data.gemini_api_key else current.get("gemini_api_key", GEMINI_API_KEY)
    }
    
    # Set model based on provider
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

@api_router.post("/admin/vouchers")
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
    return voucher

@api_router.get("/admin/vouchers")
async def admin_get_vouchers(admin: dict = Depends(get_admin_user)):
    vouchers = await db.vouchers.find({}, {"_id": 0}).to_list(100)
    return vouchers

@api_router.put("/admin/vouchers/{voucher_id}")
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

@api_router.delete("/admin/vouchers/{voucher_id}")
async def admin_delete_voucher(voucher_id: str, admin: dict = Depends(get_admin_user)):
    result = await db.vouchers.delete_one({"id": voucher_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Voucher tidak ditemukan")
    
    return {"message": "Voucher berhasil dihapus"}

# ============== MULTI-DOCUMENT GENERATION ==============

@api_router.post("/generate/multi")
async def generate_multi_documents(data: MultiGenerateRequest, user: dict = Depends(get_current_user)):
    # Check token balance
    tokens_needed = len(data.doc_types)
    if user["token_balance"] < tokens_needed:
        raise HTTPException(status_code=402, detail=f"Token tidak mencukupi. Butuh {tokens_needed} token, saldo Anda {user['token_balance']} token.")
    
    results = []
    
    # Generate each document type in the order selected by user
    for doc_type in data.doc_types:
        # Create single generate request
        single_request = GenerateRequest(
            doc_type=doc_type,
            jenjang=data.jenjang,
            kelas=data.kelas,
            kurikulum=data.kurikulum,
            semester=data.semester,
            fase=data.fase,
            mata_pelajaran=data.mata_pelajaran,
            topik=data.topik,
            alokasi_waktu=data.alokasi_waktu,
            tingkat_kesulitan=data.tingkat_kesulitan,
            jumlah_pg=data.jumlah_pg,
            jumlah_isian=data.jumlah_isian,
            jumlah_essay=data.jumlah_essay,
            sertakan_pembahasan=data.sertakan_pembahasan,
            use_custom_values=data.use_custom_values,
            resistor1=data.resistor1,
            resistor2=data.resistor2,
            voltage=data.voltage
        )
        
        # Build and send prompt
        prompt = build_prompt(single_request)
        result_html = await generate_with_gemini(prompt)
        
        # Clean up result
        result_html = re.sub(r'^```html?\n?', '', result_html)
        result_html = re.sub(r'\n?```$', '', result_html)
        
        # Save generation record
        generation_id = str(uuid.uuid4())
        generation = {
            "id": generation_id,
            "user_id": user["id"],
            "doc_type": doc_type,
            "form_data": single_request.model_dump(),
            "result_html": result_html,
            "tokens_used": 1,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.generations.insert_one(generation)
        
        results.append({
            "id": generation_id,
            "doc_type": doc_type,
            "result_html": result_html
        })
    
    # Deduct tokens
    await db.users.update_one(
        {"id": user["id"]},
        {"$inc": {"token_balance": -tokens_needed}}
    )
    
    return {
        "results": results,
        "tokens_used": tokens_needed,
        "remaining_tokens": user["token_balance"] - tokens_needed
    }

# ============== HEALTH CHECK ==============

@api_router.get("/")
async def root():
    return {"message": "ModulAI API is running", "version": "1.0.0"}

@api_router.get("/health")
async def health():
    return {"status": "healthy"}

# ============== STARTUP ==============

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
    
    # Initialize AI settings if not exists
    ai_settings = await db.settings.find_one({"key": "ai_settings"})
    if not ai_settings:
        await db.settings.insert_one({
            "key": "ai_settings",
            "value": {
                "provider": "gemini_flash_lite",
                "gemini_api_key": GEMINI_API_KEY,
                "model": "gemini-2.5-flash"
            }
        })
        logger.info("Initialized AI settings")

@app.on_event("shutdown")
async def shutdown():
    client.close()

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)
