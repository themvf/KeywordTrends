from typing import Any, Dict, List

from app.firecrawl_client import FirecrawlClient


SEARCH_QUERY_TEMPLATE = 'site:etsy.com "{keyword}"'


def find_listing_urls(client: FirecrawlClient, keyword: str, limit: int = 10) -> List[str]:
    query = SEARCH_QUERY_TEMPLATE.format(keyword=keyword)
    result = client.search(query=query, formats=["summary"], limit=limit)
    items = result.get("data", []) or result.get("results", [])
    urls = [item.get("url") for item in items if item.get("url")]
    return urls


def extract_listings(client: FirecrawlClient, urls: List[str]) -> List[Dict[str, Any]]:
    if not urls:
        return []
    schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "price": {"type": "number"},
            "currency": {"type": "string"},
            "rating": {"type": "number"},
            "review_count": {"type": "integer"},
            "tags": {"type": "array", "items": {"type": "string"}},
            "materials": {"type": "array", "items": {"type": "string"}},
            "inferred_keywords": {"type": "array", "items": {"type": "string"}},
        },
    }
    prompt = (
        "Extract Etsy listing info including title, price, currency, rating, number of reviews, "
        "list of tags, materials, and 3-7 inferred SEO keywords customers might use."
    )
    response = client.extract(urls=urls, prompt=prompt, schema=schema)
    raw = response.get("results") or response.get("data") or []
    listings: List[Dict[str, Any]] = []
    for item in raw:
        data = item.get("data", item) if isinstance(item, dict) else {}
        listings.append(
            {
                "url": item.get("url") if isinstance(item, dict) else None,
                "title": data.get("title"),
                "price": data.get("price"),
                "currency": data.get("currency"),
                "rating": data.get("rating"),
                "review_count": data.get("review_count"),
                "tags": data.get("tags"),
                "materials": data.get("materials"),
                "inferred_keywords": data.get("inferred_keywords"),
            }
        )
    return listings
