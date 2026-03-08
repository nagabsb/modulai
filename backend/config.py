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
