from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReadinessCheck:
    name: str
    passed: bool
    detail: str = ""


class V1Readiness:
    """Non-destructive readiness checks for a production deployment."""

    def evaluate(self, checks: list[ReadinessCheck]) -> dict:
        passed=sum(1 for c in checks if c.passed)
        failed=[c for c in checks if not c.passed]
        return {
            "ready": not failed,
            "passed": passed,
            "failed": len(failed),
            "checks":[c.__dict__ for c in checks],
            "blocking_reasons":[c.detail or c.name for c in failed],
        }
