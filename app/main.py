from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.posts import router as posts_router
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title='TripCast Community API',
    description='익명 커뮤니티 CRUD API 백엔드',
    version='0.1.0',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://tripcast-daejeon.netlify.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts_router, prefix='/api')

@app.get('/')
def root():
    return {'message': 'TripCast Community API is running'}
