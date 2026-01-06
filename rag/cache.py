from rag.redis_cache import RedisCache

cache = RedisCache(
    host="redis",  # "localhost" hors docker
    port=6379,
    ttl=24 * 3600
)
