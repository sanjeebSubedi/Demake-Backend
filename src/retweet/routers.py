import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src import models
from src.database import get_db
from src.dependencies import get_current_user
from src.retweet import schemas, service

router = APIRouter(prefix="/retweets", tags=["Retweets"])


@router.post(
    "",
    response_model=schemas.RetweetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_retweet(
    retweet: schemas.RetweetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Create a retweet of an existing tweet.

    A user cannot retweet their own tweets or retweet the same tweet multiple times.

    Args:
        retweet (schemas.RetweetCreate): Contains the ID of the tweet to retweet.
        db (Session): Database session instance.
        current_user (models.User): The authenticated user creating the retweet.

    Returns:
        RetweetResponse: Details of the created retweet.
            Example::

                {
                    "message": "Tweet retweeted successfully",
                    "data": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "tweet_id": "123e4567-e89b-12d3-a456-426614174000",
                        "user_id": "789e4567-e89b-12d3-a456-426614174000",
                        "created_at": "2024-03-15T14:30:00Z"
                    }
                }

    Raises:
        HTTPException:
            - 404: Tweet not found
            - 400: Cannot retweet own tweet
            - 400: Tweet already retweeted
            - 400: Tweet is deleted or unavailable

    Note:
        - Retweets appear on the user's profile and their followers' timelines
        - Original tweet author is notified of the retweet
        - Removing the original tweet will also remove all its retweets
    """
    return await service.create_retweet(
        tweet_id=retweet.tweet_id, current_user_id=current_user.id, db=db
    )


@router.delete("/{tweet_id}", status_code=status.HTTP_200_OK)
async def delete_retweet(
    tweet_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Remove a retweet from user's timeline.

    Deletes a retweet of a specific tweet by the authenticated user.
    Only the user who created the retweet can delete it.

    Args:
        tweet_id (uuid.UUID): ID of the original tweet that was retweeted.
        db (Session): Database session instance.
        current_user (models.User): The authenticated user deleting the retweet.

    Returns:
        dict: Success message.
            Example::

                {
                    "message": "Retweet deleted successfully"
                }

    Raises:
        HTTPException:
            - 404: Retweet not found
            - 403: Not authorized to remove this retweet
            - 400: Invalid tweet ID

    Note:
        - Removing a retweet doesn't affect the original tweet
    """
    return await service.delete_retweet(
        tweet_id=tweet_id, current_user_id=current_user.id, db=db
    )
