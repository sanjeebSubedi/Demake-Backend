import uuid
from datetime import datetime
from typing import Annotated, List

from pydantic import BaseModel, ConfigDict, StringConstraints


class TweetCreate(BaseModel):
    content: Annotated[str, StringConstraints(min_length=1, max_length=280)]
    parent_tweet_id: uuid.UUID | None = None


class TweetCreateResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    content: str
    created_at: datetime
    parent_tweet_id: uuid.UUID | None = None

    model_config = ConfigDict(from_attributes=True)


class TweetGet(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    content: str
    created_at: datetime
    parent_tweet_id: uuid.UUID | None = None

    model_config = ConfigDict(from_attributes=True)


class TweetsGetAll(BaseModel):
    tweets: List[TweetGet]

    model_config = ConfigDict(from_attributes=True)
