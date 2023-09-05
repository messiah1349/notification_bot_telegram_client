from abc import ABC, abstractmethod
from datetime import datetime

class AbstractBackendRequester(ABC):
    @abstractmethod
    async def get_deed_for_user(self, user_id: int):
        raise NotImplementedError

    @abstractmethod
    async def add_deed(self, user_id: int, deed_name: str):
        raise NotImplementedError
        
    @abstractmethod
    async def add_notification(self, deed_id: int, notification_time: datetime):
        raise NotImplementedError

    @abstractmethod
    async def get_deed(self, deed_id: int):
        raise NotImplementedError

    @abstractmethod
    async def mark_deed_as_done(self, deed_id: int):
        raise NotImplementedError

    @abstractmethod
    async def rename_deed(self, deed_id: int, new_name: str):
        raise NotImplementedError


