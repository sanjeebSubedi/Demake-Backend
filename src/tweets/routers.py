import uuid
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.orm import Session

from src import models
from src.database import get_db
from src.dependencies import get_current_user
from src.tweets import schemas, service
from src.tweets.exceptions import (
    EmptyTweetException,
    EmptyTweetToneRequestError,
    TweetOverflowException,
)

router = APIRouter(prefix="/tweets", tags=["tweets"])


@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=schemas.TweetCreateResponse
)
async def create_tweet(
    content: Annotated[Optional[str], Form(description="Content of the tweet")] = None,
    tone: Annotated[Optional[str], Form()] = None,
    parent_tweet_id: Annotated[Optional[uuid.UUID], Form()] = None,
    media: Annotated[Optional[UploadFile], File()] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new tweet or reply.

    Creates a new tweet, optionally with media attachment or as a reply to another tweet.
    The tone parameter can be used to modify the writing style of the tweet.

    Args:
        content (str, optional): The main text content of the tweet.
        tone (str, optional): Desired writing style for the tweet content.
        parent_tweet_id (uuid.UUID, optional): ID of the tweet being replied to.
        media (UploadFile, optional): Media file to attach to the tweet.
        current_user (models.User): The authenticated user creating the tweet.
        db (Session): Database session instance.

    Returns:
        TweetCreateResponse: Created tweet details with success message.
            Example::

                {
                    "message": "Tweet Created Successfully",
                    "data": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "content": "This is my first tweet.",
                        "media_url": "http://example.com/media/image.jpg",
                        "user_id": "789e4567-e89b-12d3-a456-426614174000",
                        "created_at": "2024-03-15T14:30:00Z",
                        "parent_tweet_id": null
                    }
                }

    Raises:
        EmptyTweetException: If neither content nor media is provided.
        EmptyTweetToneRequestError: If tone is provided without content.
        TweetOverflowException: If content exceeds 280 characters.
        HTTPException:
            - 400: Invalid parent tweet ID
            - 500: Media upload failure

    Note:
        - Content is limited to 280 characters
        - Supported media types: images, videos
        - Either content or media must be provided
        - This endpoint requires authentication
    """

    if not content or content.strip() == "":
        if tone:
            raise EmptyTweetToneRequestError
        if media == None:
            raise EmptyTweetException
    elif len(content) > 280:
        raise TweetOverflowException
    tweet = await service.create_new_tweet(
        current_user.id, content, tone, parent_tweet_id, media, db
    )
    return {"message": "Tweet Created Successfully", "data": tweet}


@router.delete("/{tweet_id}", status_code=status.HTTP_200_OK)
async def delete_tweet(
    tweet_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a tweet.

    Removes a tweet and its associated media (if any). Only the tweet owner can delete it.

    Args:
        tweet_id (uuid.UUID): ID of the tweet to delete.
        current_user (models.User): The authenticated user making the request.
        db (Session): Database session instance.

    Returns:
        dict: Success message.
            Example::

                {
                    "message": "Tweet deleted successfully!"
                }

    Raises:
        HTTPException:
            - 404: Tweet not found
            - 403: Not authorized to delete this tweet
            - 500: Error during media deletion

    Note:
        - Deleting a parent tweet will not delete its replies
        - Associated media files are also removed
        - This endpoint requires authentication
    """

    return await service.delete_tweet(tweet_id, current_user.id, db)


@router.get("/home", response_model=List[schemas.TweetHomePageResponse])
async def get_home_page_tweets(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    tab: str = Query("all", enum=["all", "following"]),
    skip: int = Query(0, ge=0),
    limit: int = Query(5, ge=1, le=100),
):
    """Get tweets for home feed.

    Retrieves tweets for the user's home timeline with pagination support.
    Can filter between all tweets or just tweets from followed users.

    Args:
        db (Session): Database session instance.
        current_user (models.User): The authenticated user viewing the feed.
        tab (str): Feed filter - "all" or "following". Defaults to "all".
        skip (int): Number of tweets to skip for pagination. Defaults to 0.
        limit (int): Maximum tweets to return. Range: 1-100. Defaults to 5.

    Returns:
        List[TweetHomePageResponse]: List of tweets with user and engagement details.
            Example::

                [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "content": "Hello everyone!",
                        "media_url": "http://example.com/media/image.jpg",
                        "created_at": "2024-03-15T14:30:00Z",
                        "user": {
                            "id": "789e4567-e89b-12d3-a456-426614174000",
                            "username": "di_caprio",
                            "full_name": "Leonardo Di Caprio",
                            "profile_image_url": "http://example.com/profile.jpg",
                            "verified_on": "2024-02-01T12:00:00Z"
                        },
                        "like_count": 42,
                        "retweet_count": 7,
                        "comment_count": 3
                    }
                ]

    Raises:
        HTTPException: 500 for internal server errors

    Note:
        - Tweets are ordered by creation date (newest first)
        - "following" tab shows only tweets from users you follow
        - Retweets are included in the feed
        - This endpoint requires authentication
    """

    return await service.get_home_page_tweets(tab, skip, limit, current_user.id, db)


@router.get("/{tweet_id}", response_model=schemas.TweetDetail)
async def get_tweet(
    tweet_id: uuid.UUID,
    db: Session = Depends(get_db),
    reply_skip: int = Query(0, ge=0),
    reply_limit: int = Query(5, ge=1, le=100),
    current_user=Depends(get_current_user),
):
    """Get detailed tweet information.

    Retrieves comprehensive information about a specific tweet, including
    replies with pagination support.

    Args:
        tweet_id (uuid.UUID): ID of the tweet to retrieve.
        db (Session): Database session instance.
        reply_skip (int): Number of replies to skip. Defaults to 0.
        reply_limit (int): Maximum replies to return. Range: 1-100. Defaults to 5.
        current_user (models.User): The authenticated user making the request.

    Returns:
        TweetDetail: Detailed tweet information including replies.
            Example::

                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "content": "Original tweet",
                    "media_url": "http://example.com/media/image.jpg",
                    "created_at": "2024-03-15T14:30:00Z",
                    "user": {
                        "id": "789e4567-e89b-12d3-a456-426614174000",
                        "username": "john_wick",
                        "full_name": "John Wick",
                        "profile_image_url": "http://example.com/profile.jpg"
                    },
                    "like_count": 42,
                    "retweet_count": 7,
                    "replies": [
                        {
                            "id": "456e4567-e89b-12d3-a456-426614174000",
                            "content": "Reply tweet",
                            "created_at": "2024-03-15T15:00:00Z",
                            "user": {
                                "username": "jane_wick",
                                "full_name": "Jane Wick"
                            }
                        }
                    ]
                }

    Raises:
        HTTPException: 404 if tweet not found

    Note:
        - Replies are ordered by creation date (newest first)
        - Includes engagement metrics (likes, retweets, replies)
        - Media URLs are included if present
        - This endpoint requires authentication
    """

    return await service.get_tweet_details(tweet_id, reply_skip, reply_limit, db)


@router.get(
    "/users/{user_id}/tweets",
    response_model=schemas.UserTweetsResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": dict, "description": "User not found"},
    },
)
async def get_user_tweets(
    user_id: Optional[uuid.UUID],
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> schemas.UserTweetsResponse:
    """Get user's tweets.

    Retrieves tweets posted by a specific user or the authenticated user
    if no user ID is provided. Excludes replies but includes retweets.

    Args:
        user_id (uuid.UUID, optional): ID of user whose tweets to retrieve.
            If None, uses authenticated user's ID.
        skip (int): Number of tweets to skip. Defaults to 0.
        limit (int): Maximum tweets to return. Defaults to 20.
        db (Session): Database session instance.
        current_user (models.User): The authenticated user making the request.

    Returns:
        UserTweetsResponse: List of user's tweets with engagement metrics.
            Example::

                {
                    "tweets": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "content": "User's tweet",
                            "media_url": "http://example.com/media/image.jpg",
                            "created_at": "2024-03-15T14:30:00Z",
                            "user": {
                                "id": "789e4567-e89b-12d3-a456-426614174000",
                                "username": "john_cena",
                                "full_name": "John Cena"
                            },
                            "likes_count": 42,
                            "retweets_count": 7,
                            "replies_count": 3
                        }
                    ]
                }

    Raises:
        HTTPException: 404 if specified user not found

    Note:
        - Tweets are ordered by creation date (newest first)
        - Replies are not included in this endpoint
        - Retweets are included
        - This endpoint requires authentication
    """

    if not user_id:
        user_id = current_user.id
    return await service.get_user_tweets(user_id, skip, limit, db)


@router.get(
    "/users/{user_id}/replies",
    response_model=schemas.UserRepliesResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": dict, "description": "User not found"},
    },
)
async def get_user_replies(
    user_id: Optional[uuid.UUID],
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> schemas.UserRepliesResponse:
    """Get user's replies.

    Retrieves reply tweets made by a specific user or the authenticated user
    if no user ID is provided. Includes details about the parent tweet.

    Args:
        user_id (uuid.UUID, optional): ID of user whose replies to retrieve.
            If None, uses authenticated user's ID.
        skip (int): Number of replies to skip. Defaults to 0.
        limit (int): Maximum replies to return. Defaults to 20.
        db (Session): Database session instance.
        current_user (models.User): The authenticated user making the request.

    Returns:
        UserRepliesResponse: List of user's replies with parent tweet details.
            Example::

                {
                    "replies": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "content": "Reply content",
                            "created_at": "2024-03-15T14:30:00Z",
                            "user": {
                                "id": "789e4567-e89b-12d3-a456-426614174000",
                                "username": "walter_white",
                                "full_name": "Walter White"
                            },
                            "likes_count": 5,
                            "retweets_count": 0,
                            "replies_count": 1,
                            "parent_tweet": {
                                "id": "456e4567-e89b-12d3-a456-426614174000",
                                "content": "Original tweet content",
                                "user": {
                                    "username": "skyler_white",
                                    "full_name": "Skyler White"
                                }
                            }
                        }
                    ]
                }

    Raises:
        HTTPException: 404 if specified user not found

    Note:
        - Replies are ordered by creation date (newest first)
        - Includes only tweets that are replies to other tweets
        - Parent tweet details are included if available
        - This endpoint requires authentication
    """

    if not user_id:
        user_id = current_user.id
    return await service.get_user_replies(user_id, skip, limit, db)
