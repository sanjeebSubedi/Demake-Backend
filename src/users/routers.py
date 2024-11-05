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
    Register a new user account.

    Allows users to create an account by providing their email, password, and other details.
    Upon successful creation, a verification email is sent asynchronously.

    **Parameters**:
        - **user** (*schemas.UserCreate*): Details required to create a new user, such as email and password.
        - **background_tasks** (*BackgroundTasks*): Manages background tasks to send verification email.
        - **db** (*Session*): Database session for performing operations.

    **Returns**:
        *CreateUserResponse*: JSON response with the new user's details.

    **Raises**:
        - **HTTPException (400)**: If the email or username already exists.

    **Example**:

    .. code-block:: json

        POST /users
        {
            "message": "User account created successfully",
            "user": {
                "id": "uuid-1234",
                "email": "user@example.com",
                "username": "newuser",
                "full_name": "New User"
            }
        }
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
    Update the profile details of the authenticated user.

    Enables users to modify profile attributes, including username, full name, bio, location, birth date,
    profile image, and header image. Only provided fields will be updated.

    **Parameters**:
        - **username** (*str*): Optional new username for the user.
        - **full_name** (*str*): Optional new full name.
        - **bio** (*str*): Optional user bio.
        - **location** (*str*): Optional location of the user.
        - **birth_date** (*datetime.date*): Optional birth date.
        - **profile_image** (*UploadFile*): Optional new profile image.
        - **header_image** (*UploadFile*): Optional new header image.
        - **current_user** (*User*): Authenticated user.
        - **db** (*Session*): Database session for performing updates.

    **Returns**:
        *UpdateUserResponse*: JSON response with updated user details.

    **Raises**:
        - **HTTPException (404)**: If the user does not exist.
        - **HTTPException (400)**: If the new username is already taken.

    **Example**:

    .. code-block:: json

        PUT /users
        {
            "id": "uuid-1234",
            "username": "updateduser",
            "full_name": "Updated Name",
            "bio": "New bio",
            "location": "New Location"
        }
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
    Verify a new user's email address using the provided token.

    Validates and activates a user's account by decoding the email from the token and setting the `verified_at` field.
    Sends a confirmation email upon successful verification.

    **Parameters**:
        - **token** (*str*): URL-safe token for email verification.
        - **background_tasks** (*BackgroundTasks*): Background task manager to send confirmation email.
        - **db** (*Session*): Database session for performing updates.

    **Returns**:
        JSON response with a success message.

    **Raises**:
        - **HTTPException (404)**: If the user associated with the token does not exist.

    **Example**:

    .. code-block:: json

        GET /users/verify/{token}
        {
            "message": "Account activated successfully"
        }
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
    Retrieve the authenticated user's profile details.

    Provides information about the currently authenticated user, including follow statistics and tweet count.

    **Parameters**:
        - **current_user** (*User*): The user retrieved from the authentication token.
        - **db** (*Session*): Database session.

    **Returns**:
        *CurrentUserDetailsResponse*: JSON response with the user's profile details.

    **Example**:

    .. code-block:: json

        GET /users/me
        {
            "id": "uuid-1234",
            "username": "currentuser",
            "full_name": "Current User",
            "num_followers": 10,
            "num_following": 20,
            "tweet_count": 5
        }
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
    """
    Retrieve the profile details of a specific user by user ID.

    Provides public details about a user, including whether they are followed by the authenticated user.

    **Parameters**:
        - **user_id** (*uuid.UUID*): ID of the user to retrieve.
        - **db** (*Session*): Database session.
        - **current_user** (*User*): The currently authenticated user.

    **Returns**:
        *UserDetailsResponse*: JSON response with the user's profile details.

    **Raises**:
        - **HTTPException (404)**: If the specified user is not found.

    **Example**:

    .. code-block:: json

        GET /users/{user_id}
        {
            "id": "uuid-1234",
            "username": "targetuser",
            "full_name": "Target User",
            "is_followed": true,
            "num_followers": 100,
            "num_following": 50,
            "tweet_count": 25
        }
    """
    follow_stats = await service.get_follow_stats(user_id=user_id, db=db)
    user_obj, is_followed = await service.get_user_details(user_id, current_user.id, db)
    user_details = schemas.UserDetailsResponse.model_validate(user_obj).model_dump()
    tweet_count = await service.get_user_total_tweet_count(db, current_user.id)
    return dict(
        user_details, is_followed=is_followed, **follow_stats, tweet_count=tweet_count
    )
