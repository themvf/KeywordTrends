from typing import Any, Dict, List, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


class InstagramClient:
    def __init__(self, access_token: str, graph_base_url: str = "https://graph.facebook.com/v21.0"):
        self.access_token = access_token
        self.graph_base_url = graph_base_url.rstrip("/")
        self._client = httpx.Client(timeout=20)

    @retry(wait=wait_exponential(min=1, max=8), stop=stop_after_attempt(3))
    def search_hashtag(self, hashtag: str, user_id: str) -> Optional[str]:
        params = {"user_id": user_id, "q": hashtag, "access_token": self.access_token}
        resp = self._client.get(f"{self.graph_base_url}/ig_hashtag_search", params=params)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("data", [])
        return items[0]["id"] if items else None

    @retry(wait=wait_exponential(min=1, max=8), stop=stop_after_attempt(3))
    def hashtag_posts(self, hashtag_id: str, fields: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        if fields is None:
            fields = "caption,media_type,media_url,permalink,like_count,comments_count"
        params = {
            "fields": fields,
            "limit": limit,
            "access_token": self.access_token,
        }
        resp = self._client.get(f"{self.graph_base_url}/{hashtag_id}/recent_media", params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", [])


def fetch_hashtag_posts(client: InstagramClient, hashtag: str, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    hashtag_id = client.search_hashtag(hashtag, user_id=user_id)
    if not hashtag_id:
        return []
    return client.hashtag_posts(hashtag_id, limit=limit)
