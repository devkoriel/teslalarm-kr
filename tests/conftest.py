# tests/conftest.py
from dotenv import load_dotenv

# Load environment variables from .env.test file (ignores if file doesn't exist)
load_dotenv(dotenv_path=".env.test")
