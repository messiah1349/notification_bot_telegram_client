import os
from dotenv import load_dotenv

load_dotenv()

TZ = 'Europe/Helsinki'
BACKEND_HOST = os.getenv('BACKEND_HOST', '')
BACKEND_PORT = os.getenv('BACKEND_PORT', '')
API_TOKEN = os.getenv('API_TOKEN', '')
