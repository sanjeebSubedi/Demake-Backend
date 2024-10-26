import uuid

from fastapi import UploadFile
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from src import models
from src.tweets import schemas
from src.tweets.exceptions import InvaildParentTweet, MediaUploadError, TweetNotFound
from src.tweets.utils import save_tweet_media


async def create_new_tweet(
    current_user_id: uuid.UUID,
    content: str,
    parent_tweet_id: uuid.UUID,
    media: UploadFile,
    db: Session,
):
    if parent_tweet_id:
        parent_tweet = (
            db.query(models.Tweet).filter(models.Tweet.id == parent_tweet_id).first()
        )
        if not parent_tweet:
            raise InvaildParentTweet
    try:
        media_path = await save_tweet_media(media, "media")
    except Exception:
        raise MediaUploadError
    new_tweet = models.Tweet(
        user_id=current_user_id,
        content=content,
        media_url=f"http://localhost:8000/{media_path}" if media_path else None,
        parent_tweet_id=(parent_tweet_id if parent_tweet_id else None),
    )

    db.add(new_tweet)
    db.commit()
    db.refresh(new_tweet)
    return new_tweet


# async def get_all_tweets(offset, limit, tweeted_after, tweeted_before, db):
#     query = db.query(models.Tweet)
#     if tweeted_after:
#         query = query.filter(models.Tweet.created_at > tweeted_after)
#     if tweeted_before:
#         query = query.filter(models.Tweet.created_at < tweeted_before)
#     query = query.order_by(desc(models.Tweet.created_at))
#     tweets = query.offset(offset).limit(limit).all()
#     return {"tweets": tweets}


async def delete_tweet(tweet_id, current_user_id, db):
    tweet = (
        db.query(models.Tweet)
        .filter(models.Tweet.id == tweet_id, models.Tweet.user_id == current_user_id)
        .first()
    )
    if not tweet:
        raise TweetNotFound
    db.delete(tweet)
    db.commit()
    return {"message": "Tweet deleted successfully!"}


async def get_home_page_tweets(
    tab: str, skip: int, limit: int, current_user_id: uuid.UUID, db: Session
):
    base_query = (
        db.query(models.Tweet, models.User)
        .join(models.User, models.Tweet.user_id == models.User.id)
        .filter(models.Tweet.parent_tweet_id == None)
        .order_by(models.Tweet.created_at.desc())
    )

    if tab == "following":
        following_subquery = (
            db.query(models.Follow.followed_id)
            .filter(models.Follow.follower_id == current_user_id)
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


async def get_tweet_details(
    tweet_id: uuid.UUID, reply_skip: int, reply_limit: int, db: Session
):
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
        raise TweetNotFound

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
