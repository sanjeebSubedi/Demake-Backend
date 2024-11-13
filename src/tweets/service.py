import os
import uuid

from fastapi import UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from src import models
from src.logger import get_logger
from src.tweets import schemas
from src.tweets.exceptions import InvaildParentTweet, MediaUploadError, TweetNotFound
from src.tweets.utils import save_tweet_media
from src.users.exceptions import UserNotFound

logger = get_logger()


async def create_new_tweet(
    current_user_id: uuid.UUID,
    content: str,
    tone: str,
    parent_tweet_id: uuid.UUID,
    media: UploadFile,
    db: Session,
):
    if parent_tweet_id:
        parent_tweet = (
            db.query(models.Tweet).filter(models.Tweet.id == parent_tweet_id).first()
        )
        if not parent_tweet:
            logger.error(f"Invalid parent tweet ID: {parent_tweet_id}")
            raise InvaildParentTweet
    try:
        media_path = await save_tweet_media(media, "media")
        logger.info(f"Media uploaded for tweet by user {current_user_id}")
    except Exception as e:
        logger.error(f"Media upload failed for tweet by user {current_user_id}: {e}")
        raise MediaUploadError
    revised_tweet = None
    if tone:
        revised_tweet = await change_tweet_tone(content, tone)
        logger.debug(f"Revised tweet with tone '{tone}': {revised_tweet}")

        # print(revised_tweet)
    new_tweet = models.Tweet(
        user_id=current_user_id,
        content=revised_tweet if revised_tweet else content,
        media_url=f"http://localhost:8000/{media_path}" if media_path else None,
        parent_tweet_id=(parent_tweet_id if parent_tweet_id else None),
    )

    db.add(new_tweet)
    db.commit()
    db.refresh(new_tweet)
    logger.info(
        f"New tweet created by user {current_user_id} with tweet ID: {new_tweet.id}"
    )
    return new_tweet


async def delete_tweet(tweet_id, current_user_id, db):
    tweet = (
        db.query(models.Tweet)
        .filter(models.Tweet.id == tweet_id, models.Tweet.user_id == current_user_id)
        .first()
    )
    if not tweet:
        logger.error(f"Tweet not found for deletion: ID {tweet_id}")
        raise TweetNotFound
    db.delete(tweet)
    db.commit()
    logger.info(f"Tweet deleted successfully: ID {tweet_id} by user {current_user_id}")
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
                media_type=(
                    None
                    if not tweet.media_url
                    else os.path.splitext(tweet.media_url)[-1].replace(".", "")
                ),
                created_at=tweet.created_at,
                user=schemas.UserInfo(
                    id=user.id,
                    username=user.username,
                    full_name=user.full_name,
                    profile_image_url=user.profile_image_url,
                    verified_on=user.verified_on,
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
            verified_on=user.verified_on,
        ),
        like_count=like_count,
        retweet_count=retweet_count,
        reply_ids=[reply_id for (reply_id,) in reply_ids],
    )
    return response


async def get_user_tweets(user_id: uuid.UUID, skip: int, limit: int, db: Session):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise UserNotFound

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

    combined_results = []

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
            "created_at": retweet.created_at,
            "user": tweet.user,
            "retweeted_by": retweet.user,
            "likes_count": len(tweet.likes),
            "retweets_count": len(tweet.retweets),
            "replies_count": len(tweet.replies),
            "is_retweet": True,
        }
        combined_results.append(retweet_response)

    combined_results.sort(key=lambda x: x["created_at"], reverse=True)
    return {"tweets": combined_results}


async def get_user_replies(user_id: uuid.UUID, skip: int, limit: int, db: Session):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise UserNotFound

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


async def change_tweet_tone(tweet, tone, parent_tweet=None):
    import ollama

    answer = ollama.generate(
        model="gemma2",
        prompt=f"Rewrite the following tweet, delimited by triple backticks, in a {tone} tone. Only return the revised tweet text with no additional commentary or explanation. ```{tweet}```",
    )
    # print(answer["response"].strip().split("\n\n")[0].strip())
    return answer["response"].strip().split("\n\n")[0].strip()
