from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    language = Column(String(2), default="ko")  # 'ko' or 'en'
    keywords = Column(JSON, default=[])  # 관심 키워드 목록
    notify_times = Column(JSON, default=[])  # 알림 수신 시간대 (예: ["09:00", "17:00"])
    notify_frequency = Column(Integer, default=1)  # 하루 알림 빈도


class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    source = Column(Text)
    title = Column(Text)
    content = Column(Text)
    url = Column(Text, unique=True)
    published = Column(Text)
    hash = Column(Text, unique=True)


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    type = Column(Text)  # 예: "price_up", "price_down", "new_model", "announcement"
    model = Column(Text)  # 해당 모델명 (예: "Model 3")
    details = Column(Text)  # 상세 내용
    source = Column(Text)  # 뉴스 출처
    url = Column(Text)  # 관련 기사 URL
    confidence = Column(Float)  # 신뢰도 (0 ~ 1)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
