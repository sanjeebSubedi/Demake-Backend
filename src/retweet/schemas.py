import uuid
from datetime import datetime

from pydantic import BaseModel


class RetweetBase(BaseModel):
    tweet_id: uuid.UUID


class RetweetCreate(RetweetBase):
    pass


class RetweetResponse(RetweetBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
