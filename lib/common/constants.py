import os

BACKEND_HOST = os.getenv('NOTIFICATION_BOT_BACKEND_HOST', '127.0.0.1')
BACKEND_PORT = os.getenv('NOTIFICATION_BOT_BACKEND_HOST', '8001')
API_TOKEN = os.getenv('NOTIFICATION_BOT_TOKEN', '214139458:AAH8UGU0PW3vUE1lRz-gjXnlB6TroUvpfUk')
TZ = os.getenv('TZ', 'Europe/Helsinki')