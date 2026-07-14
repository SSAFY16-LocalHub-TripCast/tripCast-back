# tripCast-back

TripCast 백엔드 API 서버입니다. FastAPI + SQLite 기반 익명 커뮤니티 CRUD를 제공합니다.

## 구조

- app/
  - main.py
  - routers/posts.py
  - services/post_service.py
  - models/post.py
  - schemas/post.py
  - database.py
  - config.py

## 실행

1. `.env.example`을 복사하여 `.env`로 생성합니다.
2. `pip install -r requirements.txt`
3. `uvicorn app.main:app --reload`

## API

- `GET /api/posts`
- `GET /api/posts/{post_id}`
- `POST /api/posts`
- `PUT /api/posts/{post_id}`
- `DELETE /api/posts/{post_id}`
