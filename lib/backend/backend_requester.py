from lib.backend.abs_backend_requester import AbstractBackendRequester
from telegram.request import BaseRequest

a = BaseRequest()

class BackendRequester(AbstractBackendRequester):

    def __init__(self):
        pass

    async def get_deed_for_user(user_id: int):
        raise NotImplementedError

    @abstractmethod
    async def add_deed(user_id: int, deed_name: str):
        raise NotImplementedError
        
    @abstractmethod
    async def add_notification(deed_id: int, notification_time: datetime):
        raise NotImplementedError

    @abstractmethod
    async def get_deed(deed_id: int):
        raise NotImplementedError

    @abstractmethod
    async def mark_deed_as_done(deed_id: int):
        raise NotImplementedError

    @abstractmethod
    async def rename_deed(deed_id: int, new_name: str):
        raise NotImplementedError