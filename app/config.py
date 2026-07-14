import os
from pathlib import Path
from dotenv import load_dotenv

base_dir = Path(__file__).resolve().parent.parent
load_dotenv(base_dir / '.env')

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./tripcast.db')
