from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlmodel import delete, select

from app.storage.db import get_session
from app.storage.models import (
    EtsyListing,
    InstagramPost,
    KeywordStat,
    Search,
    YouTubeVideo,
)


def platforms_key(platforms: Dict[str, bool]) -> str:
    active = [name for name, enabled in platforms.items() if enabled]
    return ",".join(sorted(active))


def get_recent_search(query: str, platforms: str, freshness_hours: int = 48) -> Optional[Search]:
    cutoff = datetime.utcnow() - timedelta(hours=freshness_hours)
    with get_session() as session:
        stmt = (
            select(Search)
            .where(Search.query == query)
            .where(Search.platforms == platforms)
            .where(Search.created_at >= cutoff)
        )
        return session.exec(stmt).first()


def list_recent_searches(limit: int = 10) -> List[Search]:
    with get_session() as session:
        stmt = select(Search).order_by(Search.created_at.desc()).limit(limit)
        return session.exec(stmt).all()


def create_search(query: str, platforms: str) -> Search:
    with get_session() as session:
        search = Search(query=query, platforms=platforms, created_at=datetime.utcnow(), status="created")
        session.add(search)
        session.commit()
        session.refresh(search)
        return search


def load_results(search_id: int) -> Dict[str, List[dict]]:
    with get_session() as session:
        yt = session.exec(select(YouTubeVideo).where(YouTubeVideo.search_id == search_id)).all()
        etsy = session.exec(select(EtsyListing).where(EtsyListing.search_id == search_id)).all()
        ig = session.exec(select(InstagramPost).where(InstagramPost.search_id == search_id)).all()
        return {
            "youtube": [video_to_row(v) for v in yt],
            "etsy": [etsy_to_row(e) for e in etsy],
            "instagram": [ig_to_row(i) for i in ig],
        }


def _replace_rows(model, search_id: int):
    with get_session() as session:
        session.exec(delete(model).where(model.search_id == search_id))
        session.commit()


def store_youtube(search_id: int, rows: List[dict]) -> None:
    _replace_rows(YouTubeVideo, search_id)
    with get_session() as session:
        for row in rows:
            video = YouTubeVideo(
                search_id=search_id,
                video_id=row.get("video_id", ""),
                title=row.get("title", ""),
                channel=row.get("channel", ""),
                views=row.get("views"),
                likes=row.get("likes"),
                published_at=row.get("published"),
                tags=row.get("tags"),
                url=row.get("url", ""),
            )
            session.add(video)
        session.commit()


def store_etsy(search_id: int, rows: List[dict]) -> None:
    _replace_rows(EtsyListing, search_id)
    with get_session() as session:
        for row in rows:
            listing = EtsyListing(
                search_id=search_id,
                listing_url=row.get("url", ""),
                title=row.get("title", ""),
                price=row.get("price"),
                currency=row.get("currency"),
                rating=row.get("rating"),
                review_count=row.get("review_count"),
                tags=row.get("tags"),
                materials=row.get("materials"),
                inferred_keywords=row.get("inferred_keywords"),
            )
            session.add(listing)
        session.commit()


def store_instagram(search_id: int, rows: List[dict]) -> None:
    _replace_rows(InstagramPost, search_id)
    with get_session() as session:
        for row in rows:
            post = InstagramPost(
                search_id=search_id,
                post_id=row.get("post_id", ""),
                caption=row.get("caption"),
                hashtags=row.get("hashtags"),
                likes=row.get("likes"),
                comments=row.get("comments"),
                media_url=row.get("media_url"),
                permalink=row.get("permalink"),
            )
            session.add(post)
        session.commit()


def video_to_row(video: YouTubeVideo) -> dict:
    return {
        "Title": video.title,
        "Channel": video.channel,
        "Views": video.views,
        "Published": video.published_at,
        "Tags": video.tags or [],
        "Link": video.url,
        "video_id": video.video_id,
    }


def etsy_to_row(listing: EtsyListing) -> dict:
    return {
        "Title": listing.title,
        "Price": listing.price,
        "Currency": listing.currency,
        "Rating": listing.rating,
        "#Reviews": listing.review_count,
        "Tags": listing.tags or [],
        "URL": listing.listing_url,
    }


def ig_to_row(post: InstagramPost) -> dict:
    return {
        "Caption": post.caption,
        "Likes": post.likes,
        "Comments": post.comments,
        "Hashtags": post.hashtags or [],
        "Link": post.permalink,
        "Thumbnail": post.media_url,
    }
