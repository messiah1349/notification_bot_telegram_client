from datetime import datetime
import json
import aiohttp

from utils.utils import Response
from lib.backend.abs_backend_requester import AbstractBackendRequester
from lib.common.constants import BACKEND_HOST, BACKEND_PORT


class BackendRequester(AbstractBackendRequester):

    def __init__(self):
        self.backend_url = f"{BACKEND_HOST}:{BACKEND_PORT}"

    async def _post(self, url: str, data: dict) -> Response:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data) as response:
                status = response.status
                text = await response.text()
        return Response(status, text)

    async def _get(self, url: str) -> Response:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                status = response.status
                text = await response.text()
        return Response(status, text)
        
    async def _patch(self, url: str, data: dict) -> Response:
        async with aiohttp.ClientSession() as session:
            async with session.patch(url, data) as response:
                status = response.status
                text = await response.text()
        return Response(status, text)

    async def get_deed_for_user(self, user_id: int) -> Response:
        url = self.backend_url + f'/user/{user_id}/deeds/'
        response = await self._get(url=url)
        return response

    async def add_deed(self, user_id: int, deed_name: str) -> Response:
        url = self.backend_url + f"/deed/add/"        
        data = {'user_id': user_id, 'deed_name': deed_name}
        data = json.dump(data)
        response = await self._post(url, data)
        return response

    async def add_notification(self, deed_id: int, notification_time: datetime) -> Response:
        url = self.backend_url + f"/deed/{deed_id}/notification/"
        data = {'notification_time': notification_time}
        data = json.dump(data)
        response = await self._patch(url, data)
        return response

    async def get_deed(self, deed_id: int) -> Response:
        url = self.backend_url + f"/deed/{deed_id}/"
        response = await self._get(url)
        return response

    async def mark_deed_as_done(self, deed_id: int) -> Response:
        url = self.backend_url + f"/deed/{deed_id}/mark_done/"
        response = await self._patch(url, None)
        return response

    async def rename_deed(self, deed_id: int, new_name: str) -> Response:
        url = self.backend_url + f"/deed/{deed_id}/rename/"
        data = {'deed_name': new_name}
        data = json.dump(data)
        response = await self._patch(url, data)
        return response