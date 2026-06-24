import time

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from polymarket.config import RATE_LIMIT_DELAY, TIMEOUT


def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in (429, 500, 502, 503, 504)
    return isinstance(exc, httpx.TransportError)


class HttpClient:
    def __init__(self, base_url: str, timeout: float = TIMEOUT, cache=None):
        self._base_url = base_url
        self._client = httpx.Client(base_url=base_url, timeout=timeout)
        self._cache = cache
        self._last_call_at = 0.0

    def get(self, path: str, params: dict | None = None, ttl: int = 0) -> dict | list:
        if self._cache and ttl > 0:
            cached = self._cache.get(self._base_url + path, params)
            if cached is not None:
                return cached
        data = self._fetch(path, params)
        if self._cache and ttl > 0:
            self._cache.set(self._base_url + path, params, data, ttl)
        return data

    def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_call_at
        if elapsed < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - elapsed)
        self._last_call_at = time.monotonic()

    @retry(
        retry=retry_if_exception(_is_retryable),
        wait=wait_exponential(multiplier=1, min=1, max=30),
        stop=stop_after_attempt(4),
        reraise=True,
    )
    def _fetch(self, path: str, params: dict | None) -> dict | list:
        self._throttle()
        response = self._client.get(path, params=params)
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *args) -> None:
        self.close()
