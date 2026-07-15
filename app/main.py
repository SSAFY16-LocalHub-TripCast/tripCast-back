from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.posts import router as posts_router
from app.routers.chat import router as chat_router
from app.services.embedding_service import initialize_ai_data
from app.database import Base, engine
from contextlib import asynccontextmanager


# DB 테이블 생성
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 시 JSON 여행 데이터를 메모리에 로딩
    initialize_ai_data()
    yield


app = FastAPI(
    title='TripCast Community API',
    description='익명 커뮤니티 + AI 여행 챗봇 API 백엔드',
    version='0.1.0',
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 기존 커뮤니티 API

app.include_router(posts_router, prefix='/api')

# AI 챗봇 API 추가
app.include_router(chat_router, prefix='/api')


@app.get('/')
def root():
    return {'message': 'TripCast API Server is running'}
