import datetime
import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import UUID4, BaseModel, ConfigDict, Field


class TweetBase(BaseModel):
    content: str
    media_url: str | None = None


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
    verified_on: Optional[datetime]

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


class UserTweetBase(BaseModel):
    id: uuid.UUID
    content: str
    media_url: Optional[str]
    created_at: datetime
    user: UserInfo
    likes_count: int = Field(default=0)
    retweets_count: int = Field(default=0)
    replies_count: int = Field(default=0)

    model_config = ConfigDict(from_attributes=True)


class RetweetInfo(UserTweetBase):
    retweeted_by: UserInfo
    is_retweet: bool = True


class TweetResponse(UserTweetBase):
    is_retweet: bool = False


class UserTweetsResponse(BaseModel):
    tweets: List[TweetResponse | RetweetInfo]

    model_config = ConfigDict(from_attributes=True)


class ReplyTweet(UserTweetBase):
    parent_tweet: Optional[UserTweetBase]


class UserRepliesResponse(BaseModel):
    replies: List[ReplyTweet]

    model_config = ConfigDict(from_attributes=True)
