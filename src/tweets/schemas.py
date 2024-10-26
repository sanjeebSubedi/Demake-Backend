import datetime
import uuid
from datetime import datetime
from typing import List

from pydantic import UUID4, BaseModel, ConfigDict


class TweetBase(BaseModel):
    content: str
    media_url: str | None = None


class TweetCreate(TweetBase):
    parent_tweet_id: uuid.UUID | None = None


class Tweet(TweetBase):
    id: UUID4
    user_id: UUID4
    parent_tweet_id: uuid.UUID | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TweetCreateResponse(BaseModel):
    message: str
    data: Tweet

    model_config = ConfigDict(from_attributes=True)


class UserInfo(BaseModel):
    id: UUID4
    username: str
    full_name: str
    profile_image_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class TweetDetail(BaseModel):
    id: UUID4
    content: str
    media_url: str | None = None
    created_at: datetime
    user: UserInfo
    like_count: int
    retweet_count: int
    reply_ids: List[UUID4]

    model_config = ConfigDict(from_attributes=True)


class TweetHomePageResponse(BaseModel):
    id: uuid.UUID
    content: str
    media_url: str | None = None
    created_at: datetime
    user: UserInfo
    like_count: int
    retweet_count: int
    comment_count: int

    model_config = ConfigDict(from_attributes=True)


class RetweetResponse(BaseModel):
    id: str
    tweet_id: str
    user_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LikeResponse(BaseModel):
    id: str
    tweet_id: str
    user_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
