from datetime import datetime
import json
import aiohttp

from lib.utils.utils import Response
from lib.backend.abs_backend_requester import AbstractBackendRequester
from lib.backend.models import Deed, AddNotification, InputDeed


class BackendRequester(AbstractBackendRequester):

    def __init__(self, backend_host: str, backend_port: str) -> Response:
        self.backend_url = f"http://{backend_host}:{backend_port}"

    async def _post(self, url: str, data: dict) -> Response:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
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
            async with session.patch(url=url, json=data) as response:
                status = response.status
                text = await response.text()
        return Response(status, text)
    
    async def _delete(self, url: str) -> Response:
        async with aiohttp.ClientSession() as session:
            async with session.delete(url=url) as response:
                status = response.status
                text = await response.text()
        return Response(status, text)

    async def get_deed_for_user(self, user_id: int) -> Response:
        url = self.backend_url + f'/user/{user_id}/deeds/'
        response = await self._get(url=url)
        deeds_src = json.loads(response.answer)
        deeds = [Deed.parse_obj(deed) for deed in deeds_src]
        return Response(response.status, deeds)

    async def add_deed(self, user_id: int, deed_name: str) -> Response:
        url = self.backend_url + f"/deed/add/"        
        data = {'telegram_id': user_id, 'deed_name': deed_name}
        InputDeed.model_validate(data)
        response = await self._post(url, data)
        return response

    async def add_notification(self, deed_id: int, notification_time: datetime) -> Response:
        url = self.backend_url + f"/deed/{deed_id}/notification/"
        data = {'notification_time': str(notification_time)}
        response = await self._patch(url, data)
        return response

    async def get_deed(self, deed_id: int) -> Response:
        url = self.backend_url + f"/deed/{deed_id}/"
        response = await self._get(url)
        deed = Deed.parse_obj(json.loads(response.answer))
        return Response(response.status, deed)

    async def mark_deed_as_done(self, deed_id: int) -> Response:
        url = self.backend_url + f"/deed/{deed_id}/"
        response = await self._delete(url)
        return response

    async def rename_deed(self, deed_id: int, new_name: str) -> Response:
        url = self.backend_url + f"/deed/{deed_id}/rename/"
        data = {'new_deed_name': new_name}
        response = await self._patch(url, data)
        return response