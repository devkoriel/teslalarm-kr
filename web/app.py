# web/app.py
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Tesla Alarm KR")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 및 템플릿 설정
static_dir = os.path.join(os.path.dirname(__file__), "static")
template_dir = os.path.join(os.path.dirname(__file__), "templates")

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=template_dir)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """기본 웹페이지 제공"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/info")
async def get_info():
    """봇 정보 API"""
    from config import SCRAPE_INTERVAL

    return {
        "name": "Tesla Alarm KR",
        "description": "테슬라 관련 뉴스와 정보를 실시간으로 제공하는 텔레그램 봇",
        "telegram_channel": "https://t.me/teslalarmKR",
        "update_interval_minutes": SCRAPE_INTERVAL // 60,
    }


@app.get("/{path:path}", response_class=HTMLResponse)
async def catch_all(request: Request, path: str):
    """SPA 라우팅을 위한 catch-all 경로"""
    if path.startswith("api/"):
        return JSONResponse({"error": "API endpoint not found"}, status_code=404)
    return templates.TemplateResponse("index.html", {"request": request})
