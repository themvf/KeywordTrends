from datetime import datetime
from typing import Optional

from sqlmodel import Column, Field, JSON, SQLModel


class Search(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    query: str
    platforms: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "created"
    notes: Optional[str] = None


class YouTubeVideo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    search_id: int = Field(foreign_key="search.id")
    video_id: str
    title: str
    channel: str
    views: Optional[int] = None
    likes: Optional[int] = None
    published_at: Optional[str] = None
    tags: Optional[list] = Field(default=None, sa_column=Column(JSON))
    url: str


class EtsyListing(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    search_id: int = Field(foreign_key="search.id")
    listing_url: str
    title: str
    price: Optional[float] = None
    currency: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    tags: Optional[list] = Field(default=None, sa_column=Column(JSON))
    materials: Optional[list] = Field(default=None, sa_column=Column(JSON))
    inferred_keywords: Optional[list] = Field(default=None, sa_column=Column(JSON))


class InstagramPost(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    search_id: int = Field(foreign_key="search.id")
    post_id: str
    caption: Optional[str] = None
    hashtags: Optional[list] = Field(default=None, sa_column=Column(JSON))
    likes: Optional[int] = None
    comments: Optional[int] = None
    media_url: Optional[str] = None
    permalink: Optional[str] = None


class KeywordStat(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    search_id: int = Field(foreign_key="search.id")
    term: str
    count_youtube: int = 0
    count_etsy: int = 0
    count_instagram: int = 0
    count_web: int = 0
    opportunity_score: float = 0.0
