import os

TZ = 'Europe/Helsinki'
BACKEND_HOST = os.getenv('BACKEND_HOST', '')
BACKEND_PORT = os.getenv('BACKEND_PORT', '')
API_TOKEN = os.getenv('NOTIFICATION_BOT_TOKEN',
                      '214139458:AAH8UGU0PW3vUE1lRz-gjXnlB6TroUvpfUk')
