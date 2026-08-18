from __future__ import annotations

from dataclasses import dataclass

from app.services.sync.models import SyncReport, SyncStatus


@dataclass(frozen=True)
class QualityGateDecision:
    approved: bool
    retryable: bool
    action: str
    report: SyncReport


class SyncQualityGate:
    def decide(self, report: SyncReport) -> QualityGateDecision:
        if report.status == SyncStatus.PASS:
            return QualityGateDecision(
                approved=True,
                retryable=False,
                action="continue",
                report=report,
            )

        if report.status == SyncStatus.WARNING:
            return QualityGateDecision(
                approved=False,
                retryable=True,
                action="adjust_timing",
                report=report,
            )

        return QualityGateDecision(
            approved=False,
            retryable=True,
            action="regenerate_or_adjust",
            report=report,
        )
