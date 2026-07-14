from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.schemas.post import PostCreate, PostDelete, PostOut, PostUpdate
from app.services.post_service import create_post, delete_post, get_post, list_posts, update_post

router = APIRouter(tags=['posts'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get('/posts', response_model=list[PostOut])
def read_posts(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return list_posts(db, skip=skip, limit=limit)


@router.get('/posts/{post_id}', response_model=PostOut)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='게시글을 찾을 수 없습니다.')
    return post


@router.post('/posts', response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_new_post(post_in: PostCreate, db: Session = Depends(get_db)):
    return create_post(db, post_in)


@router.put('/posts/{post_id}', response_model=PostOut)
def update_existing_post(post_id: int, post_in: PostUpdate, db: Session = Depends(get_db)):
    post = get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='게시글을 찾을 수 없습니다.')
    return update_post(db, post, post_in)


@router.delete('/posts/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
def remove_post(post_id: int, post_in: PostDelete, db: Session = Depends(get_db)):
    post = get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='게시글을 찾을 수 없습니다.')
    delete_post(db, post, post_in.password)
    return None
