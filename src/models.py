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
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref, relationship

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
    retweets = relationship(
        "Retweet", back_populates="user", cascade="all, delete-orphan"
    )
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    media_url = Column(String, nullable=True)
    parent_tweet_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tweets.id", ondelete="CASCADE"),
        nullable=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="tweets")
    replies = relationship(
        "Tweet",
        backref=backref("parent_tweet", remote_side=[id], passive_deletes=True),
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    retweets = relationship(
        "Retweet", back_populates="tweet", cascade="all, delete-orphan"
    )
    likes = relationship("Like", back_populates="tweet", cascade="all, delete-orphan")


class Retweet(Base):
    __tablename__ = "retweets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tweet_id = Column(
        UUID(as_uuid=True), ForeignKey("tweets.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    tweet = relationship("Tweet", back_populates="retweets")
    user = relationship("User", back_populates="retweets")

    __table_args__ = (
        UniqueConstraint("tweet_id", "user_id", name="uq_retweet_tweet_user"),
    )


class Like(Base):
    __tablename__ = "likes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tweet_id = Column(
        UUID(as_uuid=True), ForeignKey("tweets.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    tweet = relationship("Tweet", back_populates="likes")
    user = relationship("User", back_populates="likes")

    __table_args__ = (
        UniqueConstraint("tweet_id", "user_id", name="uq_like_tweet_user"),
    )


class Follow(Base):
    __tablename__ = "follows"

    follower_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    followed_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # follower = relationship(
    #     "User", foreign_keys=[follower_id], back_populates="following"
    # )
    # followed = relationship(
    #     "User", foreign_keys=[followed_id], back_populates="followers"
    # )
