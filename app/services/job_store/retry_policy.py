from __future__ import annotations


class RetryPolicy:
    def __init__(self,max_attempts: int = 3):
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        self.max_attempts=max_attempts

    def can_retry(self, attempts: int) -> bool:
        return attempts < self.max_attempts

    def next_attempt(self, attempts: int) -> int:
        if not self.can_retry(attempts):
            raise RuntimeError("Maximum retry attempts exceeded")
        return attempts+1
