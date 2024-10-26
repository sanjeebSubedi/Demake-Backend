import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, UploadFile

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm"}
MAX_FILE_SIZE = 10 * 1024 * 1024


async def save_tweet_media(
    media: Optional[UploadFile], base_path: str
) -> Optional[str]:
    """
    Save uploaded media file and return the relative path.
    Returns None if no media is provided.
    """
    if not media:
        return None

    if media.size and media.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size too large. Maximum size is {MAX_FILE_SIZE/1024/1024}MB",
        )

    if media.content_type not in ALLOWED_IMAGE_TYPES | ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only images (JPEG, PNG, GIF, WebP) and videos (MP4, WebM) are allowed",
        )

    media_dir = Path(os.path.join("static", base_path))
    media_dir.mkdir(parents=True, exist_ok=True)

    file_extension = os.path.splitext(media.filename)[1].lower()
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = media_dir / unique_filename

    try:
        contents = await media.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        return str(file_path)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to save media file: {str(e)}"
        )
