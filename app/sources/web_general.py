from typing import Any, Dict, List

from app.firecrawl_client import FirecrawlClient


def search_web(client: FirecrawlClient, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
    result = client.search(query=keyword, formats=["summary"], limit=limit)
    items = result.get("data", []) or result.get("results", [])
    return items
