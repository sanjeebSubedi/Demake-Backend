from fastapi import status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from src import models
from src.tweets.exceptions import InvaildParentTweetId, NonOwnerDelete, TweetNotFound


async def create_new_tweet(user_id, tweet_data, db: Session):
    tweet_data = tweet_data.model_dump()
    tweet_data["user_id"] = user_id
    tweet_instance = models.Tweet(**tweet_data)
    try:
        db.add(tweet_instance)
        db.commit()
        db.refresh(tweet_instance)
    except Exception as e:
        db.rollback()
        # logger.error(f"Failed to insert tweet. ForeignKey Violation: {e}")
        raise InvaildParentTweetId
    return tweet_instance


async def get_all_tweets(offset, limit, tweeted_after, tweeted_before, db):
    query = db.query(models.Tweet)
    if tweeted_after:
        query = query.filter(models.Tweet.created_at > tweeted_after)
    if tweeted_before:
        query = query.filter(models.Tweet.created_at < tweeted_before)
    query = query.order_by(desc(models.Tweet.created_at))
    tweets = query.offset(offset).limit(limit).all()
    return {"tweets": tweets}


async def delete_tweet(tweet_id, user_id, db):
    tweet = db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()
    if tweet is None:
        # logger.error(
        #     f"Failed to delete tweet. Tweet with id `{tweet_id}` does not exist."
        # )
        raise TweetNotFound(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tweet not found."
        )
    if tweet.user_id != user_id:
        # logger.warning(
        #     f"Unauthorized delete attempt. User `{user_id}` attempted to delete tweet `{tweet_id}`, but they are not the owner."
        # )
        raise NonOwnerDelete
    db.query(models.Tweet).filter(models.Tweet.parent_tweet_id == tweet_id).delete()
    db.delete(tweet)
    db.commit()
    # logger.info(f"Tweet with id `{tweet_id}` successfully deleted by user `{user_id}`.")
    return {"message": "Tweet deleted successfully."}
