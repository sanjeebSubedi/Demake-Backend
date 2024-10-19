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
    user = (
        db.query(models.User)
        .filter(models.User.email == user_credentials.username)
        .first()
    )
    if not user:
        raise InvalidCredentials

    if not user.is_verified:
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
