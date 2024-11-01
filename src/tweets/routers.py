import uuid
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.orm import Session

from src import models
from src.database import get_db
from src.dependencies import get_current_user
from src.tweets import schemas, service
from src.tweets.exceptions import EmptyTweetException, TweetOverflowException

router = APIRouter(prefix="/tweets", tags=["tweets"])


@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=schemas.TweetCreateResponse
)
async def create_tweet(
    content: Annotated[Optional[str], Form(description="Content of the tweet")] = None,
    parent_tweet_id: Annotated[Optional[uuid.UUID], Form()] = None,
    media: Annotated[Optional[UploadFile], File()] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new tweet or reply to an existing tweet.

    Allows the current user to create a new tweet or a reply to an existing tweet. Optionally, media can be attached.

    :param content: The main content of the tweet.
    :type content: str
    :param parent_tweet_id: The ID of the parent tweet if this is a reply.
    :type parent_tweet_id: Optional[uuid.UUID]
    :param media: Media file associated with the tweet.
    :type media: Optional[UploadFile]
    :param current_user: Dependency to retrieve the currently authenticated user.
    :type current_user: models.User
    :param db: Database session dependency.
    :type db: Session
    :returns: JSON response with success message and created tweet data.
    :rtype: TweetCreateResponse
    :raises HTTPException: 400 error if the tweet is empty or exceeds 280 characters, or if the parent tweet is invalid.
    :raises HTTPException: 500 error if there is an error in uploading media.

    **Example**:

    .. code-block:: json

        POST /tweets
        {
            "message": "Tweet Created Successfully",
            "data": {
                "id": "uuid-1234",
                "content": "Hello World!",
                "media_url": "http://example.com/image.jpg",
                "user_id": "user-uuid",
                "created_at": "2024-10-28T12:00:00"
            }
        }
    """

    if not content or content.strip() == "":
        if media == None:
            raise EmptyTweetException
    elif len(content) > 280:
        raise TweetOverflowException
    tweet = await service.create_new_tweet(
        current_user.id, content, parent_tweet_id, media, db
    )
    return {"message": "Tweet Created Successfully", "data": tweet}


@router.delete("/{tweet_id}", status_code=status.HTTP_200_OK)
async def delete_tweet(
    tweet_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a tweet by its ID.

    :param tweet_id: The ID of the tweet to delete.
    :type tweet_id: uuid.UUID
    :param current_user: Dependency to retrieve the currently authenticated user.
    :type current_user: models.User
    :param db: Database session dependency.
    :type db: Session
    :returns: JSON response with success message.
    :rtype: dict
    :raises HTTPException: 404 error if the tweet does not exist or is not owned by the current user.

    **Example**:

    .. code-block:: json

        DELETE /tweets/{tweet_id}
        {
            "message": "Tweet deleted successfully!"
        }
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
    """
    Retrieve tweets for the user's home page.

    Fetches tweets based on the selected tab (`all` or `following`). Supports pagination.

    :param db: Database session dependency.
    :type db: Session
    :param current_user: Dependency to retrieve the currently authenticated user.
    :type current_user: models.User
    :param tab: "all" for all tweets, "following" for tweets from followed users.
    :type tab: str
    :param skip: The number of tweets to skip (pagination).
    :type skip: int
    :param limit: Maximum number of tweets to return.
    :type limit: int
    :returns: List of tweets with detailed user and engagement information.
    :rtype: List[schemas.TweetHomePageResponse]
    :raises HTTPException: 500 error for any internal server error.

    **Example**:

    .. code-block:: json

        GET /tweets/home?tab=all&skip=0&limit=5
        [
            {
                "id": "uuid-1234",
                "content": "This is a sample tweet",
                "created_at": "2024-10-28T12:00:00",
                "user": {
                    "id": "user-uuid",
                    "username": "johndoe",
                    "full_name": "John Doe",
                    "profile_image_url": "http://example.com/profile.jpg",
                    "verified_on": null
                },
                "like_count": 10,
                "retweet_count": 2,
                "comment_count": 5
            }
        ]
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
    """
    Get detailed information of a tweet by its ID, including replies with pagination.

    :param tweet_id: The ID of the tweet to retrieve.
    :type tweet_id: uuid.UUID
    :param db: Database session dependency.
    :type db: Session
    :param reply_skip: The number of replies to skip (pagination).
    :type reply_skip: int
    :param reply_limit: Maximum number of replies to return.
    :type reply_limit: int
    :param current_user: Dependency to retrieve the currently authenticated user.
    :type current_user: models.User
    :returns: Detailed information about the tweet, including user, engagement counts, and replies.
    :rtype: schemas.TweetDetail
    :raises HTTPException: 404 error if the tweet is not found.

    **Example**:

    .. code-block:: json

        GET /tweets/{tweet_id}
        {
            "id": "uuid-1234",
            "content": "Detailed tweet content",
            "created_at": "2024-10-28T12:00:00",
            "user": {
                "id": "user-uuid",
                "username": "johndoe",
                "full_name": "John Doe",
                "profile_image_url": "http://example.com/profile.jpg"
            },
            "like_count": 100,
            "retweet_count": 20,
            "reply_ids": ["reply-uuid-1", "reply-uuid-2"]
        }
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
    """
    Retrieve tweets from a specific user, or the current user if no ID is provided.

    :param user_id: The ID of the user whose tweets to retrieve.
    :type user_id: Optional[uuid.UUID]
    :param skip: The number of tweets to skip (pagination).
    :type skip: int
    :param limit: Maximum number of tweets to return.
    :type limit: int
    :param db: Database session dependency.
    :type db: Session
    :param current_user: Dependency to retrieve the currently authenticated user.
    :type current_user: models.User
    :returns: List of tweets, including retweets but excluding replies.
    :rtype: schemas.UserTweetsResponse
    :raises HTTPException: 404 error if the specified user is not found.

    **Example**:

    .. code-block:: json

        GET /tweets/users/{user_id}/tweets
        {
            "tweets": [
                {
                    "id": "tweet-uuid",
                    "content": "Sample user tweet",
                    "created_at": "2024-10-28T12:00:00",
                    "user": {
                        "id": "user-uuid",
                        "username": "johndoe",
                        "full_name": "John Doe"
                    },
                    "likes_count": 5,
                    "retweets_count": 2,
                    "replies_count": 3
                }
            ]
        }
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
    """
    Retrieve replies made by a specific user, or the current user if no ID is provided.

    :param user_id: The ID of the user whose replies to retrieve.
    :type user_id: Optional[uuid.UUID]
    :param skip: The number of replies to skip (pagination).
    :type skip: int
    :param limit: Maximum number of replies to return.
    :type limit: int
    :param db: Database session dependency.
    :type db: Session
    :param current_user: Dependency to retrieve the currently authenticated user.
    :type current_user: models.User
    :returns: List of replies, with details of parent tweet if available.
    :rtype: schemas.UserRepliesResponse
    :raises HTTPException: 404 error if the specified user is not found.

    **Example**:

    .. code-block:: json

        GET /tweets/users/{user_id}/replies
        {
            "replies": [
                {
                    "id": "reply-uuid",
                    "content": "Sample reply",
                    "created_at": "2024-10-28T12:00:00",
                    "user": {
                        "id": "user-uuid",
                        "username": "janedoe",
                        "full_name": "Jane Doe"
                    },
                    "likes_count": 2,
                    "retweets_count": 0,
                    "replies_count": 1,
                    "parent_tweet": {
                        "id": "parent-tweet-uuid",
                        "content": "Original tweet content"
                    }
                }
            ]
        }
    """

    if not user_id:
        user_id = current_user.id
    return await service.get_user_replies(user_id, skip, limit, db)
