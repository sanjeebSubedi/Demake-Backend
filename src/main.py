from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.auth.routers import router as auth_router
from src.database import engine
from src.models import Base
from src.tweets.routers import router as tweets_router
from src.users.routers import router as users_router

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)

app.include_router(users_router)
