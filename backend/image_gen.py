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


async def generate_image(prompt: str, aspect_ratio: str = "3:2") -> str:
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
                logger.error(f"Imagen response has no predictions: {data}")
            else:
                logger.error(f"Imagen API error {resp.status_code}: {resp.text[:500]}")
    except Exception as e:
        logger.error(f"Imagen API exception: {e}")
    except Exception as e:
        logger.error(f"Imagen API exception: {e}")

    return None


def extract_questions_from_html(html: str) -> list:
    """Extract individual questions from generated soal HTML for image prompts"""
    questions = []
    # Match numbered questions: patterns like "1.", "1)", "Soal 1", etc.
    # Split by question number patterns in the HTML
    parts = re.split(r'(?=<(?:p|div|li|tr)[^>]*>\s*(?:<[^>]*>)*\s*(?:Soal\s+)?\d{1,3}[\.\)])', html)

    for part in parts[1:]:  # Skip content before first question
        # Extract text content without HTML tags
        text = re.sub(r'<[^>]+>', ' ', part)
        text = re.sub(r'\s+', ' ', text).strip()
        if len(text) > 20:  # Only meaningful content
            questions.append(text[:300])  # Limit prompt length

    return questions


def build_image_prompt(question_text: str, mata_pelajaran: str, topik: str) -> str:
    """Build an image generation prompt from a question"""
    return (
        f"Educational illustration for {mata_pelajaran} about {topik}. "
        f"Clean, simple, professional diagram or illustration suitable for an exam question. "
        f"Context: {question_text[:200]}. "
        f"Style: clean educational textbook illustration, white background, labeled diagram, "
        f"no text overlay, no watermark, suitable for Indonesian school exam."
    )


async def add_images_to_soal(html: str, mata_pelajaran: str, topik: str) -> str:
    """Generate images for each question and embed them into the HTML"""
    questions = extract_questions_from_html(html)
    if not questions:
        logger.warning("No questions extracted from HTML for image generation")
        return html

    result_html = html
    for i, q_text in enumerate(questions):
        prompt = build_image_prompt(q_text, mata_pelajaran, topik)
        logger.info(f"Generating image for question {i+1}/{len(questions)}")

        b64_image = await generate_image(prompt)
        if b64_image:
            img_tag = (
                f'<div style="margin:8px 0;text-align:center;">'
                f'<img src="data:image/png;base64,{b64_image}" '
                f'style="max-width:320px;max-height:220px;border-radius:8px;border:1px solid #e2e8f0;" '
                f'alt="Ilustrasi soal {i+1}" />'
                f'<p style="font-size:10px;color:#94a3b8;margin-top:2px;">Ilustrasi AI</p>'
                f'</div>'
            )
            # Insert image after the question number/header
            # Find the nth question marker and insert image after it
            pattern = r'(<(?:p|div|li|tr)[^>]*>\s*(?:<[^>]*>)*\s*(?:Soal\s+)?\d{1,3}[\.\)])'
            matches = list(re.finditer(pattern, result_html))
            if i < len(matches):
                insert_pos = matches[i].end()
                # Find the end of the current tag
                close_tag = result_html.find('>', insert_pos)
                if close_tag == -1:
                    close_tag = insert_pos
                else:
                    close_tag += 1
                result_html = result_html[:close_tag] + img_tag + result_html[close_tag:]

    return result_html
