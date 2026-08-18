from __future__ import annotations

import heapq
from dataclasses import dataclass,field


@dataclass(order=True)
class QueueItem:
    sort_key: tuple[int,int]
    task: object=field(compare=False)


class InMemoryTaskQueue:
    """Deterministic V1 queue boundary.

    The production implementation can be replaced by Redis, RabbitMQ,
    SQS, or another durable queue without changing worker scheduling.
    """

    def __init__(self):
        self._items=[]
        self._sequence=0

    def enqueue(self, task):
        self._sequence+=1
        # Higher priority first; FIFO within equal priority.
        heapq.heappush(
            self._items,
            QueueItem((-task.priority,self._sequence),task),
        )

    def dequeue(self):
        if not self._items:
            return None
        return heapq.heappop(self._items).task

    def __len__(self):
        return len(self._items)
