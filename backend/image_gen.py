"""Image generation using Gemini Imagen API"""
import httpx
import base64
import logging
import re
from database import db

logger = logging.getLogger(__name__)


async def get_image_api_key():
    """Get the highest priority active image generation API key"""
    key_doc = await db.image_keys.find_one(
        {"is_active": True},
        {"_id": 0},
        sort=[("priority", 1)]
    )
    if not key_doc:
        return None, None
    return key_doc.get("api_key"), key_doc.get("model", "imagen-4.0-generate-001")


async def generate_image(prompt: str) -> str:
    """Generate an image using Imagen API and return base64 data"""
    api_key, model = await get_image_api_key()
    if not api_key:
        logger.warning("No active image generation API key found")
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:predict"
    headers = {"x-goog-api-key": api_key, "Content-Type": "application/json"}
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
        }
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                predictions = data.get("predictions", [])
                if predictions:
                    b64 = predictions[0].get("bytesBase64Encoded")
                    if b64:
                        return b64
                logger.error(f"Imagen: no predictions in response")
            else:
                logger.error(f"Imagen API error {resp.status_code}: {resp.text[:500]}")
    except Exception as e:
        logger.error(f"Imagen API exception: {e}")

    return None


def build_image_prompt(question_text: str, mata_pelajaran: str, topik: str) -> str:
    """Build image prompt — simple real-world illustration, absolutely NO TEXT"""
    clean_text = re.sub(r'<[^>]+>', '', question_text)
    clean_text = re.sub(r'\$[^$]+\$', '', clean_text)
    clean_text = re.sub(r'[A-E]\.\s*\d+.*', '', clean_text)  # Remove answer choices
    clean_text = clean_text[:120].strip()

    return (
        f"Simple colorful illustration showing a real-world scene related to {topik} in {mata_pelajaran}. "
        f"Style: flat design, soft colors, educational children book illustration. "
        f"ABSOLUTE RULE: The image must contain ZERO text. No letters, no numbers, no labels, no words, no equations, no symbols, no annotations whatsoever. "
        f"Only visual elements like objects, people, nature, arrows showing motion. "
        f"Clean white background, simple composition."
    )


def split_soal_from_jawaban(html: str):
    """Split HTML into soal section and the rest (kunci jawaban, pembahasan)"""
    # Common section headers that indicate answer key starts
    answer_markers = [
        r'<h2[^>]*>.*?(?:KUNCI|Kunci)\s*(?:JAWABAN|Jawaban).*?</h2>',
        r'<h2[^>]*>.*?(?:PEMBAHASAN|Pembahasan).*?</h2>',
        r'<h2[^>]*>.*?(?:JAWABAN|Jawaban).*?</h2>',
        r'(?:II|III)\.\s*(?:KUNCI|PEMBAHASAN)',
    ]

    split_pos = len(html)
    for marker in answer_markers:
        match = re.search(marker, html, re.IGNORECASE)
        if match and match.start() < split_pos:
            split_pos = match.start()

    soal_html = html[:split_pos]
    rest_html = html[split_pos:]
    return soal_html, rest_html


def extract_question_positions(html: str):
    """Find positions of each question number in the soal HTML"""
    # Match patterns like: <p>1., <div>1), Soal 1, <li>1.
    pattern = r'(<(?:p|div|li|tr)[^>]*>\s*(?:<(?:strong|b|em)[^>]*>)*\s*(?:Soal\s+)?\d{1,3}[\.\)])'
    return list(re.finditer(pattern, html))


async def add_images_to_soal(html: str, mata_pelajaran: str, topik: str) -> str:
    """Generate images ONLY for the questions section, not for answers"""
    # Split soal from kunci jawaban/pembahasan
    soal_html, rest_html = split_soal_from_jawaban(html)

    # Find questions in soal section only
    matches = extract_question_positions(soal_html)
    if not matches:
        logger.warning("No questions found in soal section for image generation")
        return html

    logger.info(f"Found {len(matches)} questions for image generation")

    # Generate images and insert in reverse order (so positions stay valid)
    for i in range(len(matches) - 1, -1, -1):
        match = matches[i]

        # Extract question text for context (from this question to next or end)
        q_start = match.start()
        q_end = matches[i + 1].start() if i + 1 < len(matches) else len(soal_html)
        q_text = soal_html[q_start:q_end]

        prompt = build_image_prompt(q_text, mata_pelajaran, topik)
        logger.info(f"Generating image for question {i + 1}/{len(matches)}")

        b64_image = await generate_image(prompt)
        if b64_image:
            img_tag = (
                f'<div style="margin:10px 0;text-align:center;">'
                f'<img src="data:image/png;base64,{b64_image}" '
                f'style="max-width:320px;max-height:220px;border-radius:6px;'
                f'border:1px solid #e2e8f0;" '
                f'alt="Ilustrasi soal {i + 1}" />'
                f'<p style="font-size:9px;color:#94a3b8;margin:2px 0 0 0;">Ilustrasi AI</p>'
                f'</div>'
            )
            # Insert image right after the question number tag
            insert_pos = match.end()
            # Find the closing > of the current element
            close_bracket = soal_html.find('>', insert_pos)
            if close_bracket != -1:
                insert_pos = close_bracket + 1
            soal_html = soal_html[:insert_pos] + img_tag + soal_html[insert_pos:]

    return soal_html + rest_html
