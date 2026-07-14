from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate


def get_post(db: Session, post_id: int) -> Post | None:
    return db.query(Post).filter(Post.id == post_id).first()


def verify_post_password(post: Post, password: str) -> bool:
    return post.password == password


def list_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Post).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()


def create_post(db: Session, post_in: PostCreate) -> Post:
    post = Post(
        title=post_in.title,
        content=post_in.content,
        password=post_in.password,
        category='community',
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def update_post(db: Session, post: Post, post_in: PostUpdate) -> Post:
    if post.password != post_in.password:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='비밀번호가 일치하지 않습니다.')

    if post_in.title is not None:
        post.title = post_in.title
    if post_in.content is not None:
        post.content = post_in.content

    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post: Post, password: str) -> None:
    if post.password != password:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='비밀번호가 일치하지 않습니다.')

    db.delete(post)
    db.commit()
