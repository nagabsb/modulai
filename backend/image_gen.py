"""
Image generation module for Mode Bergambar.
Primary: Gemini 2.5 Flash Image (text + images in 1 call)
Fallback: Kimi soal → Imagen images
"""
import httpx
import base64
import logging
import re
from database import db
from prompts_image import build_bergambar_prompt, build_fallback_image_prompts

logger = logging.getLogger(__name__)


async def get_gemini_api_key():
    """Get Gemini API key from either image_keys or ai_keys collection"""
    # First try image_keys
    key_doc = await db.image_keys.find_one(
        {"is_active": True},
        {"_id": 0},
        sort=[("priority", 1)]
    )
    if key_doc:
        return key_doc.get("api_key")

    # Fallback to regular Gemini ai_keys
    key_doc = await db.ai_keys.find_one(
        {"is_active": True, "provider": "gemini"},
        {"_id": 0},
        sort=[("priority", 1)]
    )
    if key_doc:
        return key_doc.get("api_key")

    return None


async def generate_soal_bergambar(data) -> str:
    """
    Generate soal + gambar sekaligus pakai Gemini 2.5 Flash Image.
    Returns HTML with embedded base64 images.
    """
    api_key = await get_gemini_api_key()
    if not api_key:
        raise Exception("Tidak ada API key Gemini aktif untuk image generation")

    prompt = build_bergambar_prompt(data)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "temperature": 1.0
        }
    }

    logger.info("Calling Gemini 2.5 Flash Image for bergambar generation")

    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            resp = await client.post(url, json=payload)

            if resp.status_code != 200:
                error_text = resp.text[:500]
                logger.error(f"Gemini Flash Image API error {resp.status_code}: {error_text}")
                raise Exception(f"Gemini API error: {resp.status_code}")

            data_resp = resp.json()
            candidates = data_resp.get("candidates", [])
            if not candidates:
                raise Exception("No candidates in Gemini response")

            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                raise Exception("No parts in Gemini response")

            # Parse interleaved text + image parts into HTML
            html_parts = []
            for part in parts:
                if "text" in part:
                    html_parts.append(part["text"])
                elif "inlineData" in part:
                    mime = part["inlineData"].get("mimeType", "image/png")
                    b64 = part["inlineData"].get("data", "")
                    if b64:
                        img_html = (
                            f'<div style="margin:10px 0;text-align:center;">'
                            f'<img src="data:{mime};base64,{b64}" '
                            f'style="max-width:320px;max-height:220px;border-radius:6px;'
                            f'border:1px solid #e2e8f0;" />'
                            f'<p style="font-size:9px;color:#94a3b8;margin:2px 0 0 0;">Ilustrasi AI</p>'
                            f'</div>'
                        )
                        html_parts.append(img_html)

            result_html = "\n".join(html_parts)

            # Clean up markdown code fences if present
            result_html = re.sub(r'^```html?\n?', '', result_html)
            result_html = re.sub(r'\n?```$', '', result_html)

            img_count = result_html.count('data:image/')
            logger.info(f"Gemini Flash Image generated {img_count} images")

            return result_html

    except httpx.TimeoutException:
        logger.error("Gemini Flash Image timed out")
        raise Exception("Image generation timed out")


async def generate_image_imagen(prompt: str, api_key: str) -> str:
    """Fallback: Generate single image using Imagen API"""
    url = "https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict"
    headers = {"x-goog-api-key": api_key, "Content-Type": "application/json"}
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": 1}
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                predictions = data.get("predictions", [])
                if predictions:
                    return predictions[0].get("bytesBase64Encoded", "")
            else:
                logger.error(f"Imagen fallback error {resp.status_code}: {resp.text[:300]}")
    except Exception as e:
        logger.error(f"Imagen fallback exception: {e}")

    return ""


async def fallback_add_images(soal_html: str, mata_pelajaran: str, topik: str) -> str:
    """
    Fallback flow: Soal sudah di-generate oleh Kimi (text only).
    Sekarang extract setiap soal, buat prompt gambar spesifik, generate pakai Imagen.
    """
    api_key = await get_gemini_api_key()
    if not api_key:
        logger.warning("No API key for fallback image generation")
        return soal_html

    # Split soal from jawaban section
    answer_markers = [
        r'<h2[^>]*>.*?(?:KUNCI|Kunci)\s*(?:JAWABAN|Jawaban).*?</h2>',
        r'<h2[^>]*>.*?(?:PEMBAHASAN|Pembahasan).*?</h2>',
        r'<h2[^>]*>.*?(?:JAWABAN|Jawaban).*?</h2>',
    ]
    split_pos = len(soal_html)
    for marker in answer_markers:
        match = re.search(marker, soal_html, re.IGNORECASE)
        if match and match.start() < split_pos:
            split_pos = match.start()

    soal_part = soal_html[:split_pos]
    rest_part = soal_html[split_pos:]

    # Extract questions
    pattern = r'(<(?:p|div|li|tr)[^>]*>\s*(?:<(?:strong|b|em)[^>]*>)*\s*(?:Soal\s+)?\d{1,3}[\.\)])'
    matches = list(re.finditer(pattern, soal_part))

    if not matches:
        return soal_html

    # Extract text of each question
    soal_texts = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(soal_part)
        raw = soal_part[start:end]
        clean = re.sub(r'<[^>]+>', ' ', raw)
        clean = re.sub(r'\s+', ' ', clean).strip()
        soal_texts.append(clean)

    # Build specific image prompts
    image_prompts = build_fallback_image_prompts(soal_texts, mata_pelajaran, topik)

    # Generate images in reverse order
    for i in range(len(matches) - 1, -1, -1):
        if i < len(image_prompts):
            logger.info(f"Fallback: generating image for soal {i + 1}/{len(matches)}")
            b64 = await generate_image_imagen(image_prompts[i], api_key)
            if b64:
                img_tag = (
                    f'<div style="margin:10px 0;text-align:center;">'
                    f'<img src="data:image/png;base64,{b64}" '
                    f'style="max-width:320px;max-height:220px;border-radius:6px;'
                    f'border:1px solid #e2e8f0;" />'
                    f'<p style="font-size:9px;color:#94a3b8;margin:2px 0 0 0;">Ilustrasi AI</p>'
                    f'</div>'
                )
                insert_pos = matches[i].end()
                close = soal_part.find('>', insert_pos)
                if close != -1:
                    insert_pos = close + 1
                soal_part = soal_part[:insert_pos] + img_tag + soal_part[insert_pos:]

    return soal_part + rest_part
