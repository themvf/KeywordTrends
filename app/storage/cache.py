from datetime import datetime, timedelta
from typing import Optional

from sqlmodel import select

from app.storage.db import get_session
from app.storage.models import Search


def find_recent_search(query: str, platforms: str, freshness_hours: int = 48) -> Optional[Search]:
    cutoff = datetime.utcnow() - timedelta(hours=freshness_hours)
    with get_session() as session:
        stmt = (
            select(Search)
            .where(Search.query == query)
            .where(Search.platforms == platforms)
            .where(Search.created_at >= cutoff)
        )
        result = session.exec(stmt).first()
        return result
