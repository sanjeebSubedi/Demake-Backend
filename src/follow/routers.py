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
    """
    Follow a specific user by user ID.

    This endpoint allows the current user to follow another user.
    If the follow relationship already exists or if the target user is not found,
    an error is raised.

    Parameters
    ----------
    user_id : uuid.UUID
        Unique identifier of the user to be followed.
    db : Session
        Database session dependency.
    current_user : User
        Dependency to fetch the currently authenticated user.

    Returns
    -------
    dict
        JSON response with a success message, including the username of the followed user.

    Raises
    ------
    HTTPException
        404: If the target user does not exist.
        400: If the follow relationship already exists.

    Example
    -------
    .. code-block:: json

        POST /follow/{user_id}
        {
            "message": "You are now following {username}"
        }
    """
    return await service.follow_user(user_id, current_user.id, db)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def unfollow_user(
    user_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """
    Unfollow a previously followed user.

    This endpoint allows the current user to unfollow a specified user.
    If the follow relationship does not exist, an error is raised.

    Parameters
    ----------
    user_id : str
        Unique identifier of the user to be unfollowed.
    db : Session
        Database session dependency.
    current_user : User
        Dependency to fetch the currently authenticated user.

    Returns
    -------
    dict
        JSON response with a success message, including the username of the unfollowed user.

    Raises
    ------
    HTTPException
        400: If attempting to unfollow oneself or if the follow relationship does not exist.
        404: If the user is not found.

    Example
    -------
    .. code-block:: json

        DELETE /follow/{user_id}
        {
            "message": "You have unfollowed {username}"
        }
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
    """
    Retrieve a list of followers for a specified user or the current user.

    Parameters
    ----------
    user_id : uuid.UUID, optional
        User ID to retrieve followers for. If None, retrieves followers of the current user.
    db : Session
        Database session dependency.
    current_user : User
        Dependency to fetch the currently authenticated user.

    Returns
    -------
    FollowersDetailsResponse
        A list of follower details, including full name, username,
        bio, profile image URL, and follow status.

    Raises
    ------
    HTTPException
        400: If the specified user does not exist.

    Example
    -------
    .. code-block:: json

        GET /follow/followers
        {
            "followers": [
                {
                    "full_name": "John Doe",
                    "username": "johndoe",
                    "bio": "Lover of tech",
                    "profile_image_url": "http://example.com/image.jpg",
                    "is_followed": True
                }
            ]
        }
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
    """
    Retrieve a list of users the specified user or current user is following.

    Parameters
    ----------
    user_id : str, optional
        User ID to retrieve following details for. If None, retrieves following details of the current user.
    db : Session
        Database session dependency.
    current_user : User
        Dependency to fetch the currently authenticated user.

    Returns
    -------
    FollowingDetailsResponse
        A list of users that the current user or specified
        user is following, including full name, username,
        bio, profile image URL, and follow status.

    Raises
    ------
    HTTPException
        404: If the specified user does not exist.

    Example
    -------
    .. code-block:: json

        GET /follow/following
        {
            "following": [
                {
                    "full_name": "Jane Doe",
                    "username": "janedoe",
                    "bio": "Coffee enthusiast",
                    "profile_image_url": "http://example.com/image.jpg",
                    "is_followed": True
                }
            ]
        }
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
    """
    Fetch follow suggestions for the current user.

    This endpoint provides a list of users that the current user has not yet followed.
    The results are limited by the specified `limit`.

    Parameters
    ----------
    current_user : uuid.UUID
        Current user's unique identifier.
    db : Session
        Database session dependency.
    limit : int, optional
        Number of follow suggestions to return (default: 5).

    Returns
    -------
    List[FollowSuggestionsResponse]
        A list of suggested users to follow.

    Raises
    ------
    HTTPException
        If an internal server error occurs, raises a 500 error.

    Example
    -------
    .. code-block:: json

        GET /follow/suggestions
        [
            {
                "id": "uuid-1234",
                "full_name": "Alice Smith",
                "username": "alicesmith",
                "profile_image_url": "http://example.com/image.jpg",
                "is_followed": False
            }
        ]
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
