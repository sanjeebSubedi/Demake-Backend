from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class LikeBase(BaseModel):
    tweet_id: UUID


class LikeCreate(LikeBase):
    pass


class LikeResponse(LikeBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
