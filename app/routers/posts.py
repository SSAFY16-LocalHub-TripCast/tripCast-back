from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.schemas.post import PostCreate, PostDelete, PostOut, PostPasswordCheck, PasswordVerifyResult, PostUpdate
from app.services.post_service import create_post, delete_post, get_post, list_posts, update_post, verify_post_password

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


@router.post('/posts/{post_id}/verify-password', response_model=PasswordVerifyResult)
def verify_post_password_route(post_id: int, password_in: PostPasswordCheck, db: Session = Depends(get_db)):
    post = get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='게시글을 찾을 수 없습니다.')
    if not verify_post_password(post, password_in.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='비밀번호가 일치하지 않습니다.')
    return PasswordVerifyResult(valid=True)


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
