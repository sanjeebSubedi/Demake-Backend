import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src import models
from src.like.exceptions import AlreadyLiked, LikeNotFound, TweetNotFound


async def create_like(tweet_id: uuid.UUID, current_user_id: uuid.UUID, db: Session):
    tweet = db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()
    if not tweet:
        raise TweetNotFound

    try:
        db_like = models.Like(tweet_id=tweet_id, user_id=current_user_id)
        db.add(db_like)
        db.commit()
        db.refresh(db_like)
        return db_like
    except IntegrityError:
        db.rollback()
        raise AlreadyLiked


async def delete_like(tweet_id: uuid.UUID, current_user_id: uuid.UUID, db: Session):
    like = (
        db.query(models.Like)
        .filter(
            models.Like.tweet_id == tweet_id, models.Like.user_id == current_user_id
        )
        .first()
    )

    if not like:
        raise LikeNotFound

    db.delete(like)
    db.commit()
    return {"message": "successfully unliked the tweet."}
