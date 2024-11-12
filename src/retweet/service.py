import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src import models
from src.logger import get_logger
from src.retweet.exceptions import AlreadyRetweeted, RetweetNotFound, TweetNotFound

logger = get_logger()


async def create_retweet(tweet_id: uuid.UUID, current_user_id: uuid.UUID, db: Session):
    tweet = db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()
    if not tweet:
        logger.warning(f"Retweet failed: Tweet {tweet_id} not found")
        raise TweetNotFound

    try:
        db_retweet = models.Retweet(tweet_id=tweet_id, user_id=current_user_id)
        db.add(db_retweet)
        db.commit()
        db.refresh(db_retweet)
        logger.info(f"User {current_user_id} successfully retweeted tweet {tweet_id}")
        return db_retweet
    except IntegrityError:
        db.rollback()
        logger.warning(
            f"Retweet failed: User {current_user_id} already retweeted tweet {tweet_id}"
        )
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
        logger.warning(
            f"Retweet deletion failed: Retweet not found for user {current_user_id} on tweet {tweet_id}"
        )
        raise RetweetNotFound

    db.delete(retweet)
    db.commit()
    logger.info(
        f"User {current_user_id} successfully deleted retweet on tweet {tweet_id}"
    )
    return {"message": "Retweet deleted successfully."}
