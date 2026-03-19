from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from datetime import datetime, timezone
import uuid
import re
import httpx
import logging
import asyncio

from database import db
from config import GEMINI_API_KEY, TOKEN_PACKAGES, AI_PROVIDERS
from auth import get_current_user
from models import GenerateRequest, MultiGenerateRequest, SaveGenerationRequest
from prompts import build_prompt
from docx_export import html_to_docx

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


async def get_active_keys():
    """Get all active AI keys sorted by priority"""
    keys = await db.ai_keys.find(
        {"is_active": True}, {"_id": 0}
    ).sort("priority", 1).to_list(100)
    return keys


async def call_gemini(api_key: str, model: str, prompt: str) -> str:
    """Call Google Gemini API"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
        }
    }
    async with httpx.AsyncClient(timeout=180.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        if "candidates" in data and len(data["candidates"]) > 0:
            candidate = data["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                return candidate["content"]["parts"][0].get("text", "")
        raise Exception("Empty response from Gemini")


async def call_kimi(api_key: str, model: str, prompt: str) -> str:
    """Call Kimi/Moonshot API (OpenAI-compatible)"""
    url = "https://api.moonshot.cn/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    extra = {}
    if model == "kimi-k2.5-instant":
        model = "kimi-k2.5"
        extra = {"thinking": {"type": "disabled"}}
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Kamu adalah AI pembuat perangkat ajar pendidikan Indonesia yang ahli dan berpengalaman. Output selalu dalam format HTML yang terstruktur."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        **extra
    }
    async with httpx.AsyncClient(timeout=180.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


async def call_openai(api_key: str, model: str, prompt: str) -> str:
    """Call OpenAI API"""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Kamu adalah AI pembuat perangkat ajar pendidikan Indonesia yang ahli dan berpengalaman. Output selalu dalam format HTML yang terstruktur."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_completion_tokens": 16384,
    }
    async with httpx.AsyncClient(timeout=180.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


PROVIDER_CALLERS = {
    "gemini": call_gemini,
    "kimi": call_kimi,
    "openai": call_openai,
}


async def generate_with_ai(prompt: str) -> str:
    """Generate content using AI with multi-key fallback"""
    keys = await get_active_keys()

    # Fallback: if no keys in DB, use env GEMINI_API_KEY
    if not keys and GEMINI_API_KEY:
        keys = [{
            "id": "default",
            "provider": "gemini",
            "model": "gemini-2.5-flash",
            "api_key": GEMINI_API_KEY,
            "priority": 0,
            "label": "Default Gemini Key"
        }]

    if not keys:
        raise HTTPException(status_code=500, detail="Tidak ada API key aktif. Tambahkan key di Admin Panel → AI Settings.")

    last_error = None
    for key_config in keys:
        provider = key_config["provider"]
        caller = PROVIDER_CALLERS.get(provider)
        if not caller:
            logger.warning(f"Unknown provider: {provider}")
            continue

        try:
            logger.info(f"Trying key '{key_config.get('label', key_config['id'])}' ({provider}/{key_config['model']})")
            result = await caller(key_config["api_key"], key_config["model"], prompt)

            # Update success stats
            if key_config["id"] != "default":
                await db.ai_keys.update_one(
                    {"id": key_config["id"]},
                    {"$set": {"last_used": datetime.now(timezone.utc).isoformat(), "last_error": None},
                     "$inc": {"usage_count": 1}}
                )
            return result

        except Exception as e:
            last_error = str(e)
            logger.error(f"Key '{key_config.get('label', key_config['id'])}' failed: {last_error}")
            if key_config["id"] != "default":
                await db.ai_keys.update_one(
                    {"id": key_config["id"]},
                    {"$set": {
                        "last_error": last_error[:200],
                        "last_error_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
            continue

    raise HTTPException(status_code=500, detail=f"Semua API key gagal. Error terakhir: {last_error}")


@router.get("/packages")
async def get_packages():
    settings = await db.settings.find_one({"key": "token_packages"})
    if settings:
        return settings["value"]
    return TOKEN_PACKAGES


@router.get("/ai-providers")
async def get_ai_providers_info():
    """Get available AI providers and models with pricing"""
    return AI_PROVIDERS


# Long-running document types that need async generation
ASYNC_DOC_TYPES = {"modul", "rpp"}


async def process_generation_task(task_id: str, data_dict: dict, user_id: str):
    """Background task to generate document and store result"""
    try:
        data = GenerateRequest(**data_dict)
        prompt = build_prompt(data)
        result_html = await generate_with_ai(prompt)

        result_html = re.sub(r'^```html?\n?', '', result_html)
        result_html = re.sub(r'\n?```$', '', result_html)

        generation_id = str(uuid.uuid4())
        generation = {
            "id": generation_id,
            "user_id": user_id,
            "doc_type": data.doc_type,
            "form_data": data.model_dump(),
            "result_html": result_html,
            "tokens_used": 1,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.generations.insert_one(generation)

        await db.users.update_one(
            {"id": user_id},
            {"$inc": {"token_balance": -1}}
        )

        updated_user = await db.users.find_one({"id": user_id}, {"_id": 0})

        await db.tasks.update_one(
            {"id": task_id},
            {"$set": {
                "status": "completed",
                "result": {
                    "id": generation_id,
                    "result_html": result_html,
                    "tokens_used": 1,
                    "remaining_tokens": updated_user["token_balance"]
                },
                "completed_at": datetime.now(timezone.utc).isoformat()
            }}
        )
    except Exception as e:
        logger.error(f"Background generation failed for task {task_id}: {e}")
        await db.tasks.update_one(
            {"id": task_id},
            {"$set": {"status": "failed", "error": str(e)[:500]}}
        )


@router.get("/generate/status/{task_id}")
async def get_generation_status(task_id: str, user: dict = Depends(get_current_user)):
    """Poll for async generation result"""
    task = await db.tasks.find_one({"id": task_id, "user_id": user["id"]}, {"_id": 0})
    if not task:
        raise HTTPException(status_code=404, detail="Task tidak ditemukan")

    if task["status"] == "completed":
        # Clean up task after delivering result
        await db.tasks.delete_one({"id": task_id})
        return {"status": "completed", "result": task["result"]}
    elif task["status"] == "failed":
        await db.tasks.delete_one({"id": task_id})
        raise HTTPException(status_code=500, detail=task.get("error", "Generasi gagal"))

    return {"status": "processing"}


@router.post("/generate")
async def generate_document(data: GenerateRequest, user: dict = Depends(get_current_user)):
    # For chunk calls, skip token check/deduction
    if not data.is_chunk:
        if user["token_balance"] < 1:
            raise HTTPException(status_code=402, detail="Token tidak mencukupi. Silakan top up.")

    # For long-running doc types (modul, rpp), use async background task
    if data.doc_type in ASYNC_DOC_TYPES and not data.is_chunk:
        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "user_id": user["id"],
            "status": "processing",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.tasks.insert_one(task)

        # Start background task
        asyncio.create_task(process_generation_task(task_id, data.model_dump(), user["id"]))

        return {"task_id": task_id, "status": "processing"}

    prompt = build_prompt(data)
    result_html = await generate_with_ai(prompt)

    result_html = re.sub(r'^```html?\n?', '', result_html)
    result_html = re.sub(r'\n?```$', '', result_html)

    # For chunk calls, return only HTML without saving or deducting tokens
    if data.is_chunk:
        return {"result_html": result_html}

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


@router.post("/generate/save")
async def save_chunked_generation(data: SaveGenerationRequest, user: dict = Depends(get_current_user)):
    """Save a merged chunked generation result and deduct 1 token"""
    if user["token_balance"] < 1:
        raise HTTPException(status_code=402, detail="Token tidak mencukupi. Silakan top up.")

    generation_id = str(uuid.uuid4())
    generation = {
        "id": generation_id,
        "user_id": user["id"],
        "doc_type": data.doc_type,
        "form_data": data.form_data,
        "result_html": data.result_html,
        "tokens_used": 1,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.generations.insert_one(generation)

    await db.users.update_one(
        {"id": user["id"]},
        {"$inc": {"token_balance": -1}}
    )

    updated_user = await db.users.find_one({"id": user["id"]}, {"_id": 0})

    return {
        "id": generation_id,
        "result_html": data.result_html,
        "tokens_used": 1,
        "remaining_tokens": updated_user["token_balance"]
    }



@router.get("/export/docx/{generation_id}")
async def export_docx(generation_id: str, user: dict = Depends(get_current_user)):
    """Export a generation to proper DOCX with native Word math equations"""
    generation = await db.generations.find_one(
        {"id": generation_id, "user_id": user["id"]},
        {"_id": 0}
    )
    if not generation:
        raise HTTPException(status_code=404, detail="Dokumen tidak ditemukan")

    html_content = generation.get("result_html", "")
    form_data = generation.get("form_data", {})

    title = f"{form_data.get('doc_type', 'dokumen')}_{form_data.get('mata_pelajaran', '')}_{form_data.get('topik', '')}".replace(" ", "_")

    try:
        docx_buffer = html_to_docx(html_content, title)
    except Exception as e:
        logger.error(f"DOCX export error: {e}")
        raise HTTPException(status_code=500, detail="Gagal membuat file DOCX")

    filename = f"{title[:50]}.docx"

    return StreamingResponse(
        docx_buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )



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


@router.delete("/generations/{generation_id}")
async def delete_generation(generation_id: str, user: dict = Depends(get_current_user)):
    result = await db.generations.delete_one({"id": generation_id, "user_id": user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Dokumen tidak ditemukan")
    return {"message": "Dokumen berhasil dihapus"}


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
        result_html = await generate_with_ai(prompt)

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
