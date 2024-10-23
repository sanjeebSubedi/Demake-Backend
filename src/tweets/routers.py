import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from src import models
from src.database import get_db
from src.dependencies import get_current_user
from src.tweets import schemas, service
from src.tweets.exceptions import InvaildParentTweet, NonOwnerDelete, TweetNotFound

router = APIRouter(prefix="/tweets", tags=["tweets"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_tweet(
    tweet_data: schemas.TweetCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    parent_tweet = None
    if tweet_data.parent_tweet_id:
        parent_tweet = (
            db.query(models.Tweet)
            .filter(models.Tweet.id == tweet_data.parent_tweet_id)
            .first()
        )
        if not parent_tweet:
            raise InvaildParentTweet

    new_tweet = models.Tweet(
        user_id=current_user.id,
        content=tweet_data.content,
        media_url=tweet_data.media_url,
        parent_tweet_id=(tweet_data.parent_tweet_id if parent_tweet else None),
    )

    db.add(new_tweet)
    db.commit()
    db.refresh(new_tweet)

    return {"message": "Tweet Created Successfully"}


@router.delete("/{tweet_id}", status_code=status.HTTP_200_OK)
async def delete_tweet(
    tweet_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tweet = (
        db.query(models.Tweet)
        .filter(models.Tweet.id == tweet_id, models.Tweet.user_id == current_user.id)
        .first()
    )

    if not tweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tweet not found"
        )

    db.delete(tweet)
    db.commit()

    return {"message": "Tweet and its replies deleted successfully"}


@router.get("/home", response_model=List[schemas.TweetHomePageResponse])
def get_home_page_tweets(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    tab: str = Query("all", enum=["all", "following"]),
    skip: int = Query(0, ge=0),
    limit: int = Query(5, ge=1, le=100),
):
    base_query = (
        db.query(models.Tweet, models.User)
        .join(models.User, models.Tweet.user_id == models.User.id)
        .filter(models.Tweet.parent_tweet_id == None)  # Exclude replies
        .order_by(models.Tweet.created_at.desc())
    )

    if tab == "following":
        following_subquery = (
            db.query(models.Follow.followed_id)
            .filter(models.Follow.follower_id == current_user.id)
            .subquery()
        )
        base_query = base_query.filter(models.Tweet.user_id.in_(following_subquery))

    tweets_with_users = base_query.offset(skip).limit(limit).all()

    result = []
    for tweet, user in tweets_with_users:
        like_count = (
            db.query(func.count(models.Like.id))
            .filter(models.Like.tweet_id == tweet.id)
            .scalar()
        )
        retweet_count = (
            db.query(func.count(models.Retweet.id))
            .filter(models.Retweet.tweet_id == tweet.id)
            .scalar()
        )
        comment_count = (
            db.query(func.count(models.Tweet.id))
            .filter(models.Tweet.parent_tweet_id == tweet.id)
            .scalar()
        )

        result.append(
            schemas.TweetHomePageResponse(
                id=tweet.id,
                content=tweet.content,
                media_url=tweet.media_url,
                created_at=tweet.created_at,
                user=schemas.UserInfo(
                    id=user.id,
                    username=user.username,
                    full_name=user.full_name,
                    profile_image_url=user.profile_image_url,
                ),
                like_count=like_count,
                retweet_count=retweet_count,
                comment_count=comment_count,
            )
        )

    return result


@router.get("/{tweet_id}", response_model=schemas.TweetDetail)
def get_tweet(
    tweet_id: uuid.UUID,
    db: Session = Depends(get_db),
    reply_skip: int = Query(0, ge=0),
    reply_limit: int = Query(5, ge=1, le=100),
):
    # Query for the tweet with user details, like count, and retweet count
    tweet_query = (
        db.query(
            models.Tweet,
            models.User,
            func.count(models.Like.id).label("like_count"),
            func.count(models.Retweet.id).label("retweet_count"),
        )
        .join(models.User, models.Tweet.user_id == models.User.id)
        .outerjoin(models.Like, models.Tweet.id == models.Like.tweet_id)
        .outerjoin(models.Retweet, models.Tweet.id == models.Retweet.tweet_id)
        .filter(models.Tweet.id == tweet_id)
        .group_by(models.Tweet.id, models.User.id)
    )

    result = tweet_query.first()
    if not result:
        raise HTTPException(status_code=404, detail="Tweet not found")

    tweet, user, like_count, retweet_count = result

    reply_ids = (
        db.query(models.Tweet.id)
        .filter(models.Tweet.parent_tweet_id == tweet_id)
        .order_by(models.Tweet.created_at.desc())
        .offset(reply_skip)
        .limit(reply_limit)
        .all()
    )

    response = schemas.TweetDetail(
        id=tweet.id,
        content=tweet.content,
        media_url=tweet.media_url,
        created_at=tweet.created_at,
        user=schemas.UserInfo(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            profile_image_url=user.profile_image_url,
        ),
        like_count=like_count,
        retweet_count=retweet_count,
        reply_ids=[reply_id for (reply_id,) in reply_ids],
    )

    return response
