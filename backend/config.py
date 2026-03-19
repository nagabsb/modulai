import os

JWT_SECRET = os.environ.get('JWT_SECRET', 'default_secret')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 7

MIDTRANS_SERVER_KEY = os.environ.get('MIDTRANS_SERVER_KEY')
MIDTRANS_CLIENT_KEY = os.environ.get('MIDTRANS_CLIENT_KEY')
MIDTRANS_IS_PRODUCTION = os.environ.get('MIDTRANS_IS_PRODUCTION', 'false').lower() == 'true'

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

SUPER_ADMIN_EMAIL = os.environ.get('SUPER_ADMIN_EMAIL')
SUPER_ADMIN_PASSWORD = os.environ.get('SUPER_ADMIN_PASSWORD')

TOKEN_PACKAGES = [
    {"id": "starter", "name": "Starter", "price": 99000, "tokens": 100, "documents_estimate": 40},
    {"id": "pro", "name": "Pro", "price": 249000, "tokens": 300, "documents_estimate": 120},
    {"id": "guru", "name": "Guru", "price": 399000, "tokens": 750, "documents_estimate": 300},
    {"id": "sekolah", "name": "Sekolah", "price": 899000, "tokens": 2000, "documents_estimate": 800},
]

# All supported AI providers and models with pricing (per 1M tokens in USD)
AI_PROVIDERS = {
    "gemini": {
        "name": "Google Gemini",
        "models": {
            "gemini-2.5-flash": {"name": "Gemini 2.5 Flash", "input_price": 0.30, "output_price": 2.50, "desc": "Cepat & hemat, recommended"},
            "gemini-2.5-flash-lite": {"name": "Gemini 2.5 Flash-Lite", "input_price": 0.15, "output_price": 1.00, "desc": "Paling hemat, tugas simpel"},
            "gemini-2.5-pro": {"name": "Gemini 2.5 Pro", "input_price": 1.25, "output_price": 10.00, "desc": "Kualitas tinggi, lebih lambat"},
            "gemini-2.0-flash": {"name": "Gemini 2.0 Flash", "input_price": 0.10, "output_price": 0.40, "desc": "Murah, retire Juni 2026"},
        },
        "key_url": "https://aistudio.google.com/apikey"
    },
    "kimi": {
        "name": "Kimi (Moonshot)",
        "models": {
            "kimi-k2.5": {"name": "Kimi K2.5", "input_price": 0.60, "output_price": 3.00, "desc": "Multimodal, context 262K"},
            "kimi-k2.5-instant": {"name": "Kimi K2.5 Instant", "input_price": 0.60, "output_price": 3.00, "desc": "Cepat, tanpa thinking"},
        },
        "key_url": "https://platform.moonshot.ai"
    },
    "openai": {
        "name": "OpenAI",
        "models": {
            "gpt-4o-mini": {"name": "GPT-4o Mini", "input_price": 0.15, "output_price": 0.60, "desc": "Murah, cocok fallback"},
            "gpt-4o": {"name": "GPT-4o", "input_price": 2.50, "output_price": 10.00, "desc": "Kualitas tinggi, mahal"},
        },
        "key_url": "https://platform.openai.com/api-keys"
    },
}

# Image generation providers
IMAGE_PROVIDERS = {
    "gemini-imagen": {
        "name": "Google Imagen",
        "models": {
            "imagen-4.0-generate-001": {"name": "Imagen 4.0", "price_per_image": 0.02, "desc": "Kualitas tinggi, standard"},
            "imagen-4.0-fast-generate-001": {"name": "Imagen 4.0 Fast", "price_per_image": 0.01, "desc": "Cepat & murah"},
            "imagen-4.0-ultra-generate-001": {"name": "Imagen 4.0 Ultra", "price_per_image": 0.06, "desc": "Kualitas tertinggi"},
        },
        "key_url": "https://aistudio.google.com/apikey"
    },
}
