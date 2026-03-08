from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
import uuid
import re
import httpx
import logging

from database import db
from config import GEMINI_API_KEY, TOKEN_PACKAGES
from auth import get_current_user
from models import GenerateRequest, MultiGenerateRequest
from prompts import build_prompt

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


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


@router.get("/packages")
async def get_packages():
    settings = await db.settings.find_one({"key": "token_packages"})
    if settings:
        return settings["value"]
    return TOKEN_PACKAGES


@router.post("/generate")
async def generate_document(data: GenerateRequest, user: dict = Depends(get_current_user)):
    if user["token_balance"] < 1:
        raise HTTPException(status_code=402, detail="Token tidak mencukupi. Silakan top up.")

    prompt = build_prompt(data)
    result_html = await generate_with_gemini(prompt)

    result_html = re.sub(r'^```html?\n?', '', result_html)
    result_html = re.sub(r'\n?```$', '', result_html)

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


@router.get("/generations")
async def get_generations(user: dict = Depends(get_current_user), skip: int = 0, limit: int = 20):
    generations = await db.generations.find(
        {"user_id": user["id"]},
        {"_id": 0, "result_html": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)

    total = await db.generations.count_documents({"user_id": user["id"]})

    return {"generations": generations, "total": total}


@router.get("/generations/{generation_id}")
async def get_generation(generation_id: str, user: dict = Depends(get_current_user)):
    generation = await db.generations.find_one(
        {"id": generation_id, "user_id": user["id"]},
        {"_id": 0}
    )
    if not generation:
        raise HTTPException(status_code=404, detail="Dokumen tidak ditemukan")
    return generation


@router.post("/generate/multi")
async def generate_multi_documents(data: MultiGenerateRequest, user: dict = Depends(get_current_user)):
    tokens_needed = len(data.doc_types)
    if user["token_balance"] < tokens_needed:
        raise HTTPException(status_code=402, detail=f"Token tidak mencukupi. Butuh {tokens_needed} token, saldo Anda {user['token_balance']} token.")

    results = []

    for doc_type in data.doc_types:
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

        prompt = build_prompt(single_request)
        result_html = await generate_with_gemini(prompt)

        result_html = re.sub(r'^```html?\n?', '', result_html)
        result_html = re.sub(r'\n?```$', '', result_html)

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

    await db.users.update_one(
        {"id": user["id"]},
        {"$inc": {"token_balance": -tokens_needed}}
    )

    return {
        "results": results,
        "tokens_used": tokens_needed,
        "remaining_tokens": user["token_balance"] - tokens_needed
    }
