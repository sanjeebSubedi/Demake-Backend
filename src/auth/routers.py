from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src import models, utils
from src.auth import jwt
from src.auth.exceptions import InvalidCredentials
from src.database import get_db
from src.users.email import send_account_verification_email

router = APIRouter(prefix="", tags=["Authentication"])


@router.post("/login")
async def login(
    background_tasks: BackgroundTasks,
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Handles user login by verifying credentials and returning an access token.

    Args:
        background_tasks (BackgroundTasks): FastAPI background task manager for sending email asynchronously.
        user_credentials (OAuth2PasswordRequestForm): Dependency injection for form data. Includes 'username' (user's email) and 'password'.
        db (Session): Dependency to get the database session for performing database operations.

    Returns:
        dict: If login is successful, returns an access token and its type (bearer). If email is not verified, sends a verification email and returns a message.

    Raises:
        InvalidCredentials: If the email is not found or the password is incorrect.
    """
    user = (
        db.query(models.User)
        .filter(models.User.email == user_credentials.username)
        .first()
    )
    if not user:
        raise InvalidCredentials

    if user.verified_on is None:
        await send_account_verification_email(
            user=user, background_tasks=background_tasks
        )
        return {
            "message": "You have to verify your email before logging in. Check your email for verification link."
        }

    if not utils.verify(user_credentials.password, user.password):
        raise InvalidCredentials

    access_token = jwt.create_access_token(data={"user_id": str(user.email)})

    return {"access_token": access_token, "token_type": "bearer"}
