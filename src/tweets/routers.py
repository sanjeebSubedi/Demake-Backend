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
    """
    Create a new tweet.

    Args:
        new_tweet (schemas.TweetCreate): Data of the tweet to be created, containing fields such as content and optional parent_tweet_id for replies.
        db (Session): SQLAlchemy session for database operations.
        current_user (models.User): The currently authenticated user, obtained from the authentication system.

    Returns:
        dict: A response containing the details of the newly created tweet.

    Raises:
        InvaildParentTweetId: If the `parent_tweet_id` provided is invalid or refers to a non-existent tweet.
    """
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
    """
    Retrieve all tweets, with optional filtering and pagination.

    Args:
        offset (int, optional): Number of tweets to skip before returning results. Default is 0.
        limit (int, optional): Maximum number of tweets to return. Default is 10.
        tweeted_after (datetime, optional): Fetch tweets created after this timestamp.
        tweeted_before (datetime, optional): Fetch tweets created before this timestamp.
        db (Session): SQLAlchemy session for database operations.
        current_user (models.User): The currently authenticated user.

    Returns:
        dict: A dictionary with a list of tweets satisfying the criteria.
    """

    return await service.get_all_tweets(
        offset, limit, tweeted_after, tweeted_before, db
    )


@router.delete("/{tweet_id}", status_code=status.HTTP_200_OK)
async def delete_tweet(
    tweet_id, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """
    Delete a tweet along with all of its replies.

    Args:
        tweet_id (UUID): The ID of the tweet to be deleted.
        db (Session): SQLAlchemy session for database operations.
        current_user (models.User): The currently authenticated user, who must be the owner of the tweet.

    Returns:
        dict: A response message indicating successful deletion.

    Raises:
        TweetNotFound: If the tweet does not exist.
        NonOwnerDelete: If the authenticated user is not the owner of the tweet.
    """
    return await service.delete_tweet(tweet_id, current_user.id, db)
