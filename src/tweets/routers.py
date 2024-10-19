from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from src import models
from src.database import get_db
from src.dependencies import get_current_user
from src.tweets import schemas, service
from src.tweets.exceptions import NonOwnerDelete, TweetNotFound

router = APIRouter(prefix="/tweets", tags=["tweets"])


@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=schemas.TweetCreateResponse
)
async def create_tweet(
    new_tweet: schemas.TweetCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await service.create_new_tweet(current_user.id, new_tweet, db)


@router.get("/all", status_code=status.HTTP_200_OK, response_model=schemas.TweetsGetAll)
async def get_all_tweets(
    offset: int = 0,
    limit: int = 10,
    tweeted_after: datetime = None,
    tweeted_before: datetime = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # query = db.query(models.Tweet)
    # if tweeted_after:
    #     query = query.filter(models.Tweet.created_at > tweeted_after)

    # if tweeted_before:
    #     query = query.filter(models.Tweet.created_at < tweeted_before)

    # query = query.order_by(desc(models.Tweet.created_at))

    # tweets = query.offset(offset).limit(limit).all()
    # return {"tweets": tweets}
    return await service.get_all_tweets(
        offset, limit, tweeted_after, tweeted_before, db
    )


@router.delete("/{tweet_id}", status_code=status.HTTP_200_OK)
async def delete_tweet(
    tweet_id, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    # tweet = db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()

    # if tweet is None:
    #     raise TweetNotFound(
    #         status_code=status.HTTP_404_NOT_FOUND, detail="Tweet not found."
    #     )

    # if tweet.user_id != current_user.id:
    #     raise NonOwnerDelete

    # db.delete(tweet)
    # db.commit()

    # return {"message": "Tweet deleted successfully."}
    return await service.delete_tweet(tweet_id, current_user.id, db)
