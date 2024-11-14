from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src import models
from src.database import get_db
from src.dependencies import get_current_user
from src.like import schemas, service

router = APIRouter(prefix="/likes", tags=["Likes"])


@router.post(
    "", response_model=schemas.LikeResponse, status_code=status.HTTP_201_CREATED
)
async def create_like(
    like: schemas.LikeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Like a tweet.

    Creates a like on a specific tweet by the authenticated user.
    Users can only like a tweet once.

    Args:
        like (schemas.LikeCreate): Contains the ID of the tweet to like.
        db (Session): Database session instance.
        current_user (models.User): The authenticated user creating the like.

    Returns:
        LikeResponse: Details of the created like interaction, including the new number of total likes.
            Example::

                {
                        "like_id": "550e8400-e29b-41d4-a716-446655440000",
                        "tweet_id": "123e4567-e89b-12d3-a456-426614174000",
                        "like_count: 7,
                }

    Raises:
        HTTPException:
            - 404: Tweet not found
            - 400: Tweet already liked

    Note:
        - Like count is updated in real-time
    """
    return await service.create_like(like.tweet_id, current_user.id, db)


@router.delete("/{tweet_id}", status_code=status.HTTP_200_OK)
async def delete_like(
    tweet_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Unlike a previously liked tweet.

    Removes a like from a specific tweet by the authenticated user.

    Args:
        tweet_id (UUID): ID of the tweet to unlike.
        db (Session): Database session instance.
        current_user (models.User): The authenticated user removing the like.

    Returns:
        dict: New Like Count.
            Example::

                {
                    "like_count": 6
                }

    Raises:
        HTTPException:
            - 404: Like not found

    Note:
        - Tweet's like count is updated in real-time
    """
    return await service.delete_like(tweet_id, current_user.id, db)
