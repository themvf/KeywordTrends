from typing import Any, Dict, List, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


class FirecrawlClient:
    def __init__(self, api_key: str, base_url: str = "https://api.firecrawl.dev"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(timeout=30)

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}

    @retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(3))
    def search(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        limit: int = 10,
        scraper_options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"query": query, "pageOptions": {"limit": limit}}
        if formats:
            payload["formats"] = formats
        if scraper_options:
            payload["scrapeOptions"] = scraper_options
        resp = self._client.post(
            f"{self.base_url}/v1/search",
            json=payload,
            headers=self._headers(),
        )
        resp.raise_for_status()
        return resp.json()

    @retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(3))
    def extract(
        self,
        urls: List[str],
        prompt: str,
        schema: Dict[str, Any],
        store_in_cache: bool = True,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "urls": urls,
            "prompt": prompt,
            "schema": schema,
            "storeInCache": store_in_cache,
        }
        resp = self._client.post(
            f"{self.base_url}/v1/extract",
            json=payload,
            headers=self._headers(),
        )
        resp.raise_for_status()
        return resp.json()
