import uuid
from datetime import datetime
from enum import Enum
from typing import Annotated, List, Optional, Union

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from pydantic import StringConstraints
from sqlalchemy import desc, func, literal
from sqlalchemy.orm import Session, aliased

from src import models
from src.database import get_db
from src.dependencies import get_current_user
from src.tweets import schemas, service
from src.tweets.exceptions import (
    EmptyTweetException,
    InvaildParentTweet,
    MediaUploadError,
    NonOwnerDelete,
    TweetNotFound,
    TweetOverflowException,
)
from src.tweets.utils import save_tweet_media

router = APIRouter(prefix="/tweets", tags=["tweets"])


@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=schemas.TweetCreateResponse
)
async def create_tweet(
    content: Annotated[str, Form(description="Content of the tweet")],
    parent_tweet_id: Annotated[Optional[uuid.UUID], Form()] = None,
    media: Annotated[Optional[UploadFile], File()] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not content or len(content.strip()) == 0:
        raise EmptyTweetException
    if len(content) > 280:
        raise TweetOverflowException
    tweet = await service.create_new_tweet(
        current_user.id, content, parent_tweet_id, media, db
    )
    return {"message": "Tweet Created Successfully", "data": tweet}


@router.delete("/{tweet_id}", status_code=status.HTTP_200_OK)
async def delete_tweet(
    tweet_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await service.delete_tweet(tweet_id, current_user.id, db)


@router.get("/home", response_model=List[schemas.TweetHomePageResponse])
async def get_home_page_tweets(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    tab: str = Query("all", enum=["all", "following"]),
    skip: int = Query(0, ge=0),
    limit: int = Query(5, ge=1, le=100),
):
    return await service.get_home_page_tweets(tab, skip, limit, current_user.id, db)


@router.get("/{tweet_id}", response_model=schemas.TweetDetail)
async def get_tweet(
    tweet_id: uuid.UUID,
    db: Session = Depends(get_db),
    reply_skip: int = Query(0, ge=0),
    reply_limit: int = Query(5, ge=1, le=100),
):
    return await service.get_tweet_details(tweet_id, reply_skip, reply_limit, db)


from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy.orm import joinedload


class UserInfo(BaseModel):
    id: UUID
    username: str
    full_name: str
    profile_image_url: Optional[str]
    verified_on: Optional[datetime]

    class Config:
        orm_mode = True


class TweetBase(BaseModel):
    id: UUID
    content: str
    media_url: Optional[str]
    created_at: datetime
    user: UserInfo
    likes_count: int = Field(default=0)
    retweets_count: int = Field(default=0)
    replies_count: int = Field(default=0)

    class Config:
        orm_mode = True


class RetweetInfo(TweetBase):
    retweeted_by: UserInfo
    is_retweet: bool = True


class TweetResponse(TweetBase):
    is_retweet: bool = False


class UserTweetsResponse(BaseModel):
    tweets: List[TweetResponse | RetweetInfo]

    class Config:
        orm_mode = True


class ReplyTweet(TweetBase):
    parent_tweet: Optional[TweetBase]


class UserRepliesResponse(BaseModel):
    replies: List[ReplyTweet]

    class Config:
        orm_mode = True


@router.get(
    "/users/{user_id}/tweets",
    response_model=UserTweetsResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": dict, "description": "User not found"},
    },
)
async def get_user_tweets(
    user_id: UUID, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)
) -> UserTweetsResponse:
    # Check if user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Get user's original tweets (non-replies)
    tweets_query = (
        db.query(models.Tweet)
        .filter(models.Tweet.user_id == user_id, models.Tweet.parent_tweet_id.is_(None))
        .options(
            joinedload(models.Tweet.user),
            joinedload(models.Tweet.likes),
            joinedload(models.Tweet.retweets),
            joinedload(models.Tweet.replies),
        )
    )

    # Get user's retweets
    retweets_query = (
        db.query(models.Tweet)
        .join(models.Retweet)
        .filter(models.Retweet.user_id == user_id)
        .options(
            joinedload(models.Tweet.user),
            joinedload(models.Tweet.likes),
            joinedload(models.Tweet.retweets),
            joinedload(models.Tweet.replies),
        )
    )

    # Combine and order results
    combined_results = []

    # Add original tweets
    tweets = tweets_query.offset(skip).limit(limit).all()
    for tweet in tweets:
        tweet_response = {
            "id": tweet.id,
            "content": tweet.content,
            "media_url": tweet.media_url,
            "created_at": tweet.created_at,
            "user": tweet.user,
            "likes_count": len(tweet.likes),
            "retweets_count": len(tweet.retweets),
            "replies_count": len(tweet.replies),
            "is_retweet": False,
        }
        combined_results.append(tweet_response)

    # Add retweets
    retweets = retweets_query.offset(skip).limit(limit).all()
    for tweet in retweets:
        retweet = (
            db.query(models.Retweet)
            .filter(
                models.Retweet.tweet_id == tweet.id, models.Retweet.user_id == user_id
            )
            .first()
        )

        retweet_response = {
            "id": tweet.id,
            "content": tweet.content,
            "media_url": tweet.media_url,
            "created_at": retweet.created_at,  # Use retweet timestamp
            "user": tweet.user,  # Original tweet creator
            "retweeted_by": retweet.user,  # User who retweeted
            "likes_count": len(tweet.likes),
            "retweets_count": len(tweet.retweets),
            "replies_count": len(tweet.replies),
            "is_retweet": True,
        }
        combined_results.append(retweet_response)

    # Sort combined results by created_at
    combined_results.sort(key=lambda x: x["created_at"], reverse=True)

    return {"tweets": combined_results}


@router.get(
    "/users/{user_id}/replies",
    response_model=UserRepliesResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": dict, "description": "User not found"},
    },
)
async def get_user_replies(
    user_id: UUID, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)
) -> UserRepliesResponse:
    # Check if user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Get user's replies
    replies = (
        db.query(models.Tweet)
        .filter(
            models.Tweet.user_id == user_id, models.Tweet.parent_tweet_id.isnot(None)
        )
        .options(
            joinedload(models.Tweet.user),
            joinedload(models.Tweet.parent_tweet).joinedload(models.Tweet.user),
            joinedload(models.Tweet.likes),
            joinedload(models.Tweet.retweets),
            joinedload(models.Tweet.replies),
        )
        .order_by(models.Tweet.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Prepare response
    replies_response = []
    for reply in replies:
        reply_data = {
            "id": reply.id,
            "content": reply.content,
            "media_url": reply.media_url,
            "created_at": reply.created_at,
            "user": reply.user,
            "likes_count": len(reply.likes),
            "retweets_count": len(reply.retweets),
            "replies_count": len(reply.replies),
            "parent_tweet": reply.parent_tweet,
        }
        replies_response.append(reply_data)

    return {"replies": replies_response}
