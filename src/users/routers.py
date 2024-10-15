from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.database import get_db
from src.dependencies import get_current_user
from src.models import User
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
    "", status_code=status.HTTP_200_OK, response_model=schemas.CreateUserResponse
)
async def update_user_account(
    updated_details: schemas.UserUpdate,
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
        updated_details, current_user_id=current_user.id, db=db
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
        - The user's account is activated by setting the `is_verified` flag to True.
        - After activation, a confirmation email is sent asynchronously.
    """
    await service.activate_user_account(token, db, background_tasks)
    return JSONResponse({"message": "Account is activated successfully."})
