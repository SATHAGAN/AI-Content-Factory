from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class ScheduleSlot:
    scheduled_at: datetime
    content_format: str
    sequence: int


class DynamicSchedulePlanner:
    """Build deterministic daily production slots from channel targets.

    Targets are supplied by the caller, so there is no hard-coded 5/2
    production quota. The default windows are intentionally configurable.
    """

    def build_day(
        self,
        start: datetime,
        shorts_target: int,
        long_target: int,
        shorts_start_hour: int = 9,
        shorts_end_hour: int = 17,
        long_start_hour: int = 18,
        long_end_hour: int = 21,
    ) -> list[ScheduleSlot]:
        if shorts_target < 0 or long_target < 0:
            raise ValueError("Targets cannot be negative")
        if not 0 <= shorts_start_hour <= 23 or not 0 <= shorts_end_hour <= 23:
            raise ValueError("Short window hours must be between 0 and 23")
        if not 0 <= long_start_hour <= 23 or not 0 <= long_end_hour <= 23:
            raise ValueError("Long window hours must be between 0 and 23")
        if shorts_target and shorts_end_hour < shorts_start_hour:
            raise ValueError("Short window cannot cross midnight")
        if long_target and long_end_hour < long_start_hour:
            raise ValueError("Long window cannot cross midnight")

        slots: list[ScheduleSlot] = []
        slots.extend(self._window_slots(
            start, shorts_target, "short", shorts_start_hour, shorts_end_hour
        ))
        slots.extend(self._window_slots(
            start, long_target, "long", long_start_hour, long_end_hour
        ))
        return sorted(slots, key=lambda slot: (slot.scheduled_at, slot.content_format, slot.sequence))

    @staticmethod
    def _window_slots(
        day: datetime, target: int, content_format: str, start_hour: int, end_hour: int
    ) -> list[ScheduleSlot]:
        if target == 0:
            return []
        start = day.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        end = day.replace(hour=end_hour, minute=0, second=0, microsecond=0)
        if target == 1:
            return [ScheduleSlot(start, content_format, 1)]

        interval = (end - start) / (target - 1)
        return [
            ScheduleSlot(start + interval * index, content_format, index + 1)
            for index in range(target)
        ]
