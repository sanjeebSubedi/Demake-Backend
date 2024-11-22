import datetime
import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import StringConstraints
from sqlalchemy.orm import Session

from src import models
from src.database import get_db
from src.dependencies import get_current_user
from src.users import schemas, service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=schemas.CreateUserResponse
)
async def create_user_account(
    user: schemas.UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Create a new user account.

    Registers a new user with the provided email and password. An email verification
    link is sent to the user's email address after successful registration.

    Args:
        user (schemas.UserCreate): User registration data containing email, password,
            username, and full name.
        background_tasks (BackgroundTasks): FastAPI background tasks manager for
            sending verification email.
        db (Session): Database session instance.

    Returns:
        CreateUserResponse: Newly created user details with success message.
            Example::

                {
                    "message": "User account created successfully",
                    "user": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "email": "user@example.com",
                        "username": "newuser",
                        "full_name": "New User"
                    }
                }

    Raises:
        HTTPException:
            - 400: Email or username already exists
            - 500: Email service failure

    Note:
        - Email verification is required to activate the account
        - Username must be unique
        - Password must meet minimum requirements
    """
    return await service.create_user_account(user, db, background_tasks)


@router.put(
    "", status_code=status.HTTP_200_OK, response_model=schemas.UpdateUserResponse
)
async def update_user_account(
    username: Annotated[str, Form()] = None,
    full_name: Annotated[str, Form()] = None,
    bio: Annotated[str, Form()] = None,
    location: Annotated[str, Form()] = None,
    birth_date: Annotated[datetime.date, Form()] = None,
    profile_image: Annotated[Optional[UploadFile], File()] = None,
    header_image: Annotated[Optional[UploadFile], File()] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update authenticated user's profile information.

    Updates one or more profile fields for the currently authenticated user.
    Only the provided fields will be updated, leaving others unchanged.

    Args:
        username (str, optional): New username to set.
        full_name (str, optional): New full name to set.
        bio (str, optional): New biography text.
        location (str, optional): New location information.
        birth_date (datetime.date, optional): New birth date.
        profile_image (UploadFile, optional): New profile picture to upload.
        header_image (UploadFile, optional): New header/banner image to upload.
        current_user (models.User): The authenticated user making the update.
        db (Session): Database session instance.

    Returns:
        UpdateUserResponse: Updated user profile information.
            Example::

                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "username": "updateduser",
                    "full_name": "Updated Name",
                    "bio": "My new bio",
                    "location": "Ruston, LA",
                    "birth_date": "1990-01-01",
                    "profile_image_url": "https://example.com/images/profile.jpg",
                    "header_image_url": "https://example.com/images/header.jpg"
                }

    Raises:
        HTTPException:
            - 400: Username already taken
            - 404: User not found
            - 400: Invalid image format
            - 500: Image upload failure

    Note:
        - Supported image formats: JPG, PNG, GIF
        - Maximum image size: 10MB for profile, 10MB for header
        - Username must remain unique across all users
    """
    return await service.update_user_details(
        username,
        full_name,
        bio,
        location,
        birth_date,
        profile_image,
        header_image,
        current_user.id,
        db,
    )


@router.get("/verify/{token}", status_code=status.HTTP_200_OK)
async def verify_user(
    token: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """Verify user's email address using the verification token.

    Validates the email verification token and activates the user's account.
    Sends a confirmation email upon successful verification.

    Args:
        token (str): Email verification token from the verification link.
        background_tasks (BackgroundTasks): FastAPI background tasks manager for
            sending confirmation email.
        db (Session): Database session instance.

    Returns:
        JSONResponse: Success message upon verification.
            Example::

                {
                    "message": "Account is activated successfully."
                }

    Raises:
        HTTPException:
            - 404: Invalid or expired token
            - 400: Account already verified
            - 500: Email service failure

    Note:
        - Verification tokens expire after 24 hours
        - Account features are limited until email is verified
    """
    await service.activate_user_account(token, db, background_tasks)
    return JSONResponse({"message": "Account is activated successfully."})


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=schemas.CurrentUserDetailsResponse,
)
async def get_current_user_details(
    current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get detailed profile information for the authenticated user.

    Retrieves comprehensive profile information including follower statistics,
    tweet count, and profile media URLs for the currently authenticated user.

    Args:
        current_user (models.User): The authenticated user requesting their details.
        db (Session): Database session instance.

    Returns:
        CurrentUserDetailsResponse: Complete user profile information.
            Example::

                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "username": "currentuser",
                    "full_name": "Current User",
                    "bio": "My bio",
                    "location": "City",
                    "birth_date": "1990-01-01",
                    "profile_image_url": "https://example.com/images/profile.jpg",
                    "header_image_url": "https://example.com/images/header.jpg",
                    "num_followers": 10,
                    "num_following": 20,
                    "tweet_count": 5,
                    "verified_at": "2024-03-15T14:30:00Z"
                }

    Note:
        - Requires authentication
        - Follower counts are updated in real-time
        - Tweet count includes both tweets and replies
    """

    follow_stats = await service.get_follow_stats(current_user.id, db)
    user_details = schemas.CurrentUserDetailsResponse.model_validate(
        current_user
    ).model_dump()
    tweet_count = await service.get_user_total_tweet_count(db, current_user.id)
    return dict(user_details, **follow_stats, tweet_count=tweet_count)


@router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.UserDetailsResponse,
)
async def get_user_details(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get information of a specific user.

    Retrieves profile information, follower statistics, and the follow
    relationship status between the authenticated user and the requested user.

    Args:
        user_id (uuid.UUID): ID of the user whose details are being requested.
        db (Session): Database session instance.
        current_user (models.User): The authenticated user making the request.

    Returns:
        UserDetailsResponse: User profile information and relationship status.
            Example::

                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "username": "targetuser",
                    "full_name": "Target User",
                    "bio": "User bio",
                    "location": "City",
                    "profile_image_url": "https://example.com/images/profile.jpg",
                    "header_image_url": "https://example.com/images/header.jpg",
                    "is_followed": true,
                    "num_followers": 100,
                    "num_following": 50,
                    "tweet_count": 25
                }

    Raises:
        HTTPException:
            - 404: User not found

    Note:
        - Requires authentication
        - Some profile fields may be hidden based on user privacy settings
        - Follow status is relative to the authenticated user
    """
    follow_stats = await service.get_follow_stats(user_id=user_id, db=db)
    user_obj, is_followed = await service.get_user_details(user_id, current_user.id, db)
    user_details = schemas.UserDetailsResponse.model_validate(user_obj).model_dump()
    tweet_count = await service.get_user_total_tweet_count(db, current_user.id)
    return dict(
        user_details, is_followed=is_followed, **follow_stats, tweet_count=tweet_count
    )
