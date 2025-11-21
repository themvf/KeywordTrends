from typing import Any, Dict, List, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


class YouTubeClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self._client = httpx.Client(timeout=20)

    @retry(wait=wait_exponential(min=1, max=8), stop=stop_after_attempt(3))
    def search_videos(
        self,
        query: str,
        max_results: int = 10,
        language: str = "en",
        order: str = "relevance",
    ) -> List[str]:
        params = {
            "part": "id",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "relevanceLanguage": language,
            "key": self.api_key,
            "order": order,
        }
        resp = self._client.get(f"{self.base_url}/search", params=params)
        resp.raise_for_status()
        data = resp.json()
        return [item["id"]["videoId"] for item in data.get("items", []) if "videoId" in item.get("id", {})]

    @retry(wait=wait_exponential(min=1, max=8), stop=stop_after_attempt(3))
    def get_video_details(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        if not video_ids:
            return []
        params = {
            "part": "snippet,contentDetails,statistics",
            "id": ",".join(video_ids),
            "key": self.api_key,
        }
        resp = self._client.get(f"{self.base_url}/videos", params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("items", [])


def fetch_videos(
    client: YouTubeClient,
    keyword: str,
    max_results: int = 10,
    language: str = "en",
    order: str = "relevance",
) -> List[Dict[str, Any]]:
    ids = client.search_videos(keyword, max_results=max_results, language=language, order=order)
    return client.get_video_details(ids)
