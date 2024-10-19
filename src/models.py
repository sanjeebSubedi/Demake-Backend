import uuid

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    full_name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    bio = Column(Text, nullable=True)
    location = Column(String(100), nullable=True)
    profile_image_url = Column(Text, nullable=True)
    header_image_url = Column(Text, nullable=True)
    birth_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    verified_on = Column(DateTime(timezone=True), nullable=True)

    tweets = relationship("Tweet", back_populates="user", cascade="all, delete-orphan")

    following = relationship(
        "Follow",
        backref="follower",
        foreign_keys="[Follow.follower_id]",
        cascade="all, delete-orphan",
    )

    followers = relationship(
        "Follow",
        backref="followed",
        foreign_keys="[Follow.followed_id]",
        cascade="all, delete-orphan",
    )


class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    parent_tweet_id = Column(UUID(as_uuid=True), ForeignKey("tweets.id"), nullable=True)

    user = relationship("User", back_populates="tweets")
    replies = relationship(
        "Tweet",
        remote_side=[id],
        backref="parent_tweet",
        cascade="all",
    )


class Follow(Base):
    __tablename__ = "follows"

    follower_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    followed_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
