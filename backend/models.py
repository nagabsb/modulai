from pydantic import BaseModel, EmailStr
from typing import List, Optional, Any


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
    doc_type: str
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


class MultiGenerateRequest(BaseModel):
    doc_types: List[str]
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
    provider: str
    gemini_api_key: Optional[str] = None


class VoucherUpdate(BaseModel):
    is_active: Optional[bool] = None
