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
    """
    Create a new user account.

    Args:
        user (schemas.UserCreate): Data required to create the user, including email and password.
        background_tasks (BackgroundTasks): Background task manager to send the verification email.
        db (Session): SQLAlchemy session for database operations.

    Returns:
        dict: A response containing the newly created user's details.

    Raises:
        EmailTakenException: If an account with the same email already exists.
        UsernameTakenException: If the username violates unique constraints during insertion.

    Notes:
        - The user's password is hashed before being stored in the database.
        - An account verification email is sent to the user's email asynchronously.
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
    """
    Update an authenticated user's profile details.

    Allows the user to update their username, bio, location, and birth date.
    Only the provided fields in the request body will be updated.

    Parameters:
    - user_id (str): The ID of the user to update.
    - updated_user (UserUpdate): The fields to update in the user's profile.
    - db (Session): Database session dependency.
    - current_user: The authenticated user making the request.

    Returns:
    - 200 OK: On successful update, returns a success message and the updated user details.

    Raises:
    - 404 Not Found: If the user with the specified ID does not exist.
    - 400 Bad Request: If a username conflict occurs.
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
    """
    Verify a user's account using the token sent to their email.

    Args:
        token (str): URL-safe token for email verification.
        background_tasks (BackgroundTasks): Background task manager to send the confirmation email.
        db (Session): SQLAlchemy session for database operations.

    Returns:
        JSONResponse: A message indicating the successful activation of the account.

    Raises:
        UserNotFound: If no user is found with the email decoded from the token.

    Notes:
        - The user's account is activated by setting the `verified_at` field to the verification date.
        - After activation, a confirmation email is sent asynchronously.
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
    """
    Get the details of the currently authenticated user.

    Args:
        current_user (models.User): The user retrieved from the authentication token.
        db (Session): The database session.

    Returns:
        JSON response containing the user's details.
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
    follow_stats = await service.get_follow_stats(user_id=user_id, db=db)
    user_obj, is_followed = await service.get_user_details(user_id, current_user.id, db)
    user_details = schemas.UserDetailsResponse.model_validate(user_obj).model_dump()
    tweet_count = await service.get_user_total_tweet_count(db, current_user.id)
    return dict(
        user_details, is_followed=is_followed, **follow_stats, tweet_count=tweet_count
    )
