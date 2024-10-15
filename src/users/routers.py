from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.database import get_db
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
