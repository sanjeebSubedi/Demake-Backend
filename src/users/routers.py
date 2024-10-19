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
    return await service.create_user_account(user, db, background_tasks)


@router.get("/verify/{token}", status_code=status.HTTP_200_OK)
async def verify_user(
    token: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    await service.activate_user_account(token, db, background_tasks)
    return JSONResponse({"message": "Account is activated successfully."})
