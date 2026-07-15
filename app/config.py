import os
from pathlib import Path
from dotenv import load_dotenv

base_dir = Path(__file__).resolve().parent.parent
load_dotenv(base_dir / '.env')

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./tripcast.db')

# 챗봇(AI) 관련 설정
# 실제 키가 없으면(또는 'test-'로 시작하면) ai_service.py 가 자동으로 mock 답변으로 동작합니다.
AI_API_KEY = os.getenv('AI_API_KEY', 'test-api-key')
