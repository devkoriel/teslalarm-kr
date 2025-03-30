# tests/conftest.py
from dotenv import load_dotenv

# .env.test 파일의 환경변수를 로드 (파일이 없으면 무시됨)
load_dotenv(dotenv_path=".env.test")
