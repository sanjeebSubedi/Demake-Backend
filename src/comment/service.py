from fastapi import status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from src import models
from src.comment.exceptions import InvaildCommentId, NonOwnerDelete, CommentNotFound

async def create_new_comment(user_id, comment_data, db:Session):
    comment_data = comment_data.model_dump()
    comment_data["user_id"] = user_id
    comment_instance=models.Comment(**comment_data)
    try:
        db.add(comment_instance)
        db.commit()
        db.refresh(comment_instance)
    except Exception as e:
        db.rollback()
        # logger.error(f"Failed to insert comment. ForeignKey Violation: {e}")
        raise InvaildCommentId
    return comment_instance    


async def get_all_comments(offset, limit,db):
    query=db.query(models.Comment)
    query = query.order_by(desc(models.Comment.created_at))
    comments = query.offset(offset).limit(limit).all()
    return {"comments": comments}

