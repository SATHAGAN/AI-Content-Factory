from __future__ import annotations

from app.services.recovery.controller import SelfHealingController


def build_recovery_controller(generator, evaluator, max_attempts: int = 2):
    return SelfHealingController(
        generator=generator,
        evaluator=evaluator,
        max_attempts=max_attempts,
    )
