import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.dependencies import get_current_user
from src.follow import schemas, service

router = APIRouter(prefix="/follow", tags=["Follow"])


@router.post("/{user_id}", status_code=status.HTTP_201_CREATED)
async def follow_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Follow a specific user.

    Creates a new follow relationship between the authenticated user and the target user.

    Args:
        user_id (uuid.UUID): The unique ID of the user to follow.
        db (Session): Database session instance.
        current_user (User): The authenticated user making the request.

    Returns:
        dict: A dictionary containing a success message with the followed user's username.
            Example::

                {
                    "message": "You are now following python_developer"
                }

    Raises:
        HTTPException:
            - 404: Target user not found
            - 400: Follow relationship already exists
            - 400: Attempting to follow oneself

    Note:
        This endpoint requires authentication.

    Example:
        .. code-block:: python

            import requests

            response = requests.post(
                "api/follow/123e4567-e89b-12d3-a456-426614174000",
                headers={"Authorization": "Bearer <token>"}
            )
    """
    return await service.follow_user(user_id, current_user.id, db)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def unfollow_user(
    user_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Unfollow a user.

    Removes an existing follow relationship between the authenticated user and the target user.

    Args:
        user_id (str): The unique identifier of the user to unfollow.
        db (Session): Database session instance.
        current_user (User): The authenticated user making the request.

    Returns:
        dict: A dictionary containing a success message with the unfollowed user's username.
            Example::

                {
                    "message": "You have unfollowed java_developer"
                }

    Raises:
        HTTPException:
            - 404: Target user not found
            - 400: Follow relationship does not exist
            - 400: Attempting to unfollow oneself

    Note:
        This endpoint requires authentication.

    Example:
        .. code-block:: python

            import requests

            response = requests.delete(
                "api/follow/123e4567-e89b-12d3-a456-426614174000",
                headers={"Authorization": "Bearer <token>"}
            )
    """
    return await service.unfollow_user(user_id, current_user.id, db)


@router.get(
    "/followers",
    status_code=status.HTTP_200_OK,
    response_model=schemas.FollowersDetailsResponse,
)
async def get_followers(
    user_id: uuid.UUID | None = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve a list of followers.

    Gets a list of users who follow either the authenticated user or a specified user.

    Args:
        user_id (uuid.UUID, optional): The ID of the user whose followers to retrieve.
            If None, returns followers of the authenticated user.
        current_user (User): The authenticated user making the request.
        db (Session): Database session instance.

    Returns:
        FollowersDetailsResponse: A Pydantic model containing a list of follower details.
            Example::

                {
                    "followers": [
                        {
                            "full_name": "Sanjeeb Subedi",
                            "username": "sanjeebsubedi",
                            "bio": "lazy person",
                            "profile_image_url": "http://example.com/lazy.jpg",
                            "is_followed": true
                        }
                    ]
                }

    Raises:
        HTTPException:
            - 404: Specified user not found

    Note:
        - The `is_followed` field indicates whether the authenticated user follows each follower
        - This endpoint requires authentication

    Example:
        .. code-block:: python

            import requests

            # Get followers of a specific user
            response = requests.get(
                "api/follow/followers?user_id=123e4567-e89b-12d3-a456-426614174000",
                headers={"Authorization": "Bearer <token>"}
            )

            # Get followers of the authenticated user
            response = requests.get(
                "api/follow/followers",
                headers={"Authorization": "Bearer <token>"}
            )
    """
    return await service.get_followers_details(user_id, current_user.id, db)


@router.get(
    "/following",
    status_code=status.HTTP_200_OK,
    response_model=schemas.FollowingDetailsResponse,
)
async def get_following(
    user_id: str | None = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve a list of followed users.

    Gets a list of users followed by either the authenticated user or a specified user.

    Args:
        user_id (str, optional): The ID of the user whose following list to retrieve.
            If None, returns the authenticated user's following list.
        current_user (User): The authenticated user making the request.
        db (Session): Database session instance.

    Returns:
        FollowingDetailsResponse: A Pydantic model containing a list of following details.
            Example::

                {
                    "following": [
                        {
                            "full_name": "Sanjeeb Subedi",
                            "username": "sanjeebsubedi",
                            "bio": "burnt out",
                            "profile_image_url": "http://example.com/me.jpg",
                            "is_followed": true
                        }
                    ]
                }

    Raises:
        HTTPException:
            - 404: Specified user not found

    Note:
        - The `is_followed` field indicates whether the authenticated user follows each user
        - This endpoint requires authentication

    Example:
        .. code-block:: python

            import requests

            # Get users followed by a specific user
            response = requests.get(
                "/follow/following?user_id=123e4567-e89b-12d3-a456-426614174000",
                headers={"Authorization": "Bearer <token>"}
            )

            # Get users followed by the authenticated user
            response = requests.get(
                "/follow/following",
                headers={"Authorization": "Bearer <token>"}
            )
    """
    return await service.get_following_details(user_id, current_user.id, db)


@router.get(
    "/suggestions",
    response_model=List[schemas.FollowSuggestionsResponse],
    summary="Get follow suggestions",
    description="Returns a list of users that the current user might want to follow",
)
async def follow_suggestions(
    current_user: uuid.UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 5,
):
    """Get user follow suggestions.

    Provides a list of suggested users that the authenticated user might want to follow.

    Args:
        current_user (uuid.UUID): The authenticated user's ID.
        db (Session): Database session instance.
        limit (int, optional): Maximum number of suggestions to return. Defaults to 5.

    Returns:
        List[FollowSuggestionsResponse]: A list of Pydantic models containing user suggestions.
            Example::

                [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "full_name": "Sanjeeb Subedi",
                        "username": "sanjeebsubedi",
                        "profile_image_url": "http://example.com/image.jpg",
                        "is_followed": false
                    }
                ]

    Raises:
        HTTPException:
            - 500: Internal server error while fetching suggestions

    Note:
        - Suggestions exclude users that are already being followed
        - The `is_followed` field will always be false for suggested users
        - This endpoint requires authentication

    Example:
        .. code-block:: python

            import requests

            # Get 5 follow suggestions (default)
            response = requests.get(
                "/follow/suggestions",
                headers={"Authorization": "Bearer <token>"}
            )

            # Get 10 follow suggestions
            response = requests.get(
                "/follow/suggestions?limit=10",
                headers={"Authorization": "Bearer <token>"}
            )
    """
    try:
        suggestions = await service.get_follow_suggestions(
            current_user_id=current_user.id, db=db, limit=limit
        )

        if not suggestions:
            return []

        return suggestions

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while fetching follow suggestions",
        )
