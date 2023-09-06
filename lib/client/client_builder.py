from lib.client.client import Client
from lib.backend import BackendRequester
from lib.common.constants import API_TOKEN, BACKEND_HOST, BACKEND_PORT

backend = BackendRequester(BACKEND_HOST, BACKEND_PORT)
client_app = Client(API_TOKEN, backend)
