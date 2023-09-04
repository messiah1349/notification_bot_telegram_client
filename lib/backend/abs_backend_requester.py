from abc import ABC, abstractmethod
from datetime import datetime

class AbstractBackendRequester(ABC):
    @abstractmethod
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


