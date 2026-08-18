from __future__ import annotations
from dataclasses import dataclass


@dataclass
class QuotaState:
    used: dict[str,int]


class DailyQuotaManager:
    def __init__(self):
        self._states: dict[tuple[str,str],QuotaState]={}

    def can_publish(self, channel_id: str, content_type: str, quota: dict) -> bool:
        limit=int(quota.get(content_type,0))
        used=self._states.get((channel_id,content_type),QuotaState({})).used.get("count",0)
        return used < limit

    def record(self, channel_id: str, content_type: str, quota: dict) -> None:
        if not self.can_publish(channel_id,content_type,quota):
            raise RuntimeError(f"Daily quota reached for {channel_id}/{content_type}")
        key=(channel_id,content_type)
        state=self._states.setdefault(key,QuotaState({"count":0}))
        state.used["count"] += 1

    def reset_channel(self, channel_id: str) -> None:
        for key in list(self._states):
            if key[0]==channel_id:
                del self._states[key]

    def usage(self, channel_id: str) -> dict:
        return {
            content_type:state.used.get("count",0)
            for (cid,content_type),state in self._states.items()
            if cid==channel_id
        }
