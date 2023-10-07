import imp
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Deed(BaseModel):
    id: int
    telegram_id: int
    name: str
    create_time: Optional[datetime]
    notify_time: Optional[datetime]
    done_flag: bool


class InputDeed(BaseModel):
    deed_name: str
    telegram_id: int


class AddNotification(BaseModel):
    notification_time: datetime