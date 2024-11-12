from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class LikeBase(BaseModel):
    tweet_id: UUID


class LikeCreate(LikeBase):
    pass


class LikeResponse(LikeBase):
    like_id: UUID
    tweet_id: UUID
    like_count: int

    class Config:
        from_attributes = True
