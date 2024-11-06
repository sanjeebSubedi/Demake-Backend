from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.auth.routers import router as auth_router
from src.database import engine
from src.follow.routers import router as follow_router
from src.like.routers import router as likes_router
from src.models import Base
from src.tweets.routers import router as tweets_router
from src.users.routers import router as users_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

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
app.include_router(auth_router)
app.include_router(tweets_router)
app.include_router(follow_router)
app.include_router(likes_router)
