import redis
import json
import hashlib
from typing import Any

class RedisCache:
    def __init__(
        self,
        host="localhost",
        port=6379,
        db=0,
        prefix="rag",
        ttl=86400
    ):
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )
        self.prefix = prefix
        self.ttl = ttl

    def _make_key(self, query: str, extra: dict | None = None) -> str:
        payload = {
            "query": query.strip().lower(),
            "extra": extra or {}
        }
        raw = json.dumps(payload, sort_keys=True)
        digest = hashlib.sha256(raw.encode()).hexdigest()
        return f"{self.prefix}:{digest}"

    def get(self, query: str, extra: dict | None = None) -> Any | None:
        key = self._make_key(query, extra)
        value = self.client.get(key)
        return json.loads(value) if value else None

    def set(self, query: str, value: Any, extra: dict | None = None):
        key = self._make_key(query, extra)
        self.client.setex(
            key,
            self.ttl,
            json.dumps(value)
        )
