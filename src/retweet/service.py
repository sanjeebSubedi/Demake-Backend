import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src import models
from src.retweet.exceptions import AlreadyRetweeted, RetweetNotFound, TweetNotFound


async def create_retweet(tweet_id: uuid.UUID, current_user_id: uuid.UUID, db: Session):
    tweet = db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()
    if not tweet:
        raise TweetNotFound

    try:
        db_retweet = models.Retweet(tweet_id=tweet_id, user_id=current_user_id)
        db.add(db_retweet)
        db.commit()
        db.refresh(db_retweet)
        return db_retweet
    except IntegrityError:
        db.rollback()
        raise AlreadyRetweeted


async def delete_retweet(tweet_id: uuid.UUID, current_user_id: uuid.UUID, db: Session):
    retweet = (
        db.query(models.Retweet)
        .filter(
            models.Retweet.tweet_id == tweet_id,
            models.Retweet.user_id == current_user_id,
        )
        .first()
    )

    if not retweet:
        raise RetweetNotFound

    db.delete(retweet)
    db.commit()
    return {"message": "Retweet deleted successfully."}
