from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from threading import Lock


@dataclass(frozen=True)
class DailyQuota:
    shorts_limit: int = 0
    long_limit: int = 0


class InMemoryDailyQuota:
    """Dynamic quota gate used by the scheduler.

    Limits are per channel and can be changed without code changes.
    """

    def __init__(self):
        self._counts: dict[tuple[str, date, str], int] = {}
        self._lock = Lock()

    def can_publish(self, channel_id: str, content_format: str, quota: DailyQuota, day: date) -> bool:
        limit = quota.shorts_limit if content_format == "short" else quota.long_limit
        if limit <= 0:
            return False
        with self._lock:
            return self._counts.get((channel_id, day, content_format), 0) < limit

    def consume(self, channel_id: str, content_format: str, quota: DailyQuota, day: date) -> bool:
        if not self.can_publish(channel_id, content_format, quota, day):
            return False
        with self._lock:
            key = (channel_id, day, content_format)
            self._counts[key] = self._counts.get(key, 0) + 1
        return True

    def count(self, channel_id: str, content_format: str, day: date) -> int:
        return self._counts.get((channel_id, day, content_format), 0)
