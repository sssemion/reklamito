
from typing import Any, cast

from django.conf import settings
from django.utils.functional import LazyObject, cached_property
from redis import StrictRedis


class RedisClient:
    @cached_property
    def _redis(self) -> StrictRedis:
        ssl: dict[str, Any] = {}
        if settings.REDIS_SSL_CERTIFICATE_PATH:
            ssl |= {
                'ssl': True,
                'ssl_ca_certs': settings.REDIS_SSL_CERTIFICATE_PATH,
            }
        return StrictRedis(
            db=settings.REDIS_DATABASE,
            password=settings.REDIS_PASSWORD,
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            **ssl,
        )


    def increment_shows(self, banner_id: int) -> None:
        self._redis.incr(f'banner:{banner_id}:shows')

    def get_shows(self, banner_id: int) -> int:
        return int(self._redis.get(f'banner:{banner_id}:shows') or 0)  # pyright: ignore

    def increment_clicks(self, banner_id: int) -> None:
        self._redis.incr(f'banner:{banner_id}:clicks')

    def get_clicks(self, banner_id: int) -> int:
        return int(self._redis.get(f'banner:{banner_id}:clicks') or 0)  # pyright: ignore



class LazyRedisClient(LazyObject):
    def _setup(self) -> None:
        self._wrapped = RedisClient()


REDIS_CLIENT = cast(RedisClient, LazyRedisClient())
