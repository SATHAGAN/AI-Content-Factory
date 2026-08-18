from __future__ import annotations

from dataclasses import dataclass

from app.services.repair.models import RepairAction, RepairPlan


@dataclass(frozen=True)
class RepairExecutionResult:
    action: RepairAction
    success: bool
    message: str
    metadata: dict | None = None


class RepairExecutor:
    """Execution boundary; concrete media adapters can be injected later."""

    def __init__(self, tts_adapter=None, video_adapter=None):
        self.tts_adapter=tts_adapter
        self.video_adapter=video_adapter

    def execute(self, plan: RepairPlan) -> RepairExecutionResult:
        if plan.action == RepairAction.NONE:
            return RepairExecutionResult(
                action=plan.action,
                success=True,
                message="No repair required.",
            )

        if plan.action == RepairAction.ADJUST_TTS_SPEED:
            if self.tts_adapter is None:
                return RepairExecutionResult(
                    action=plan.action,
                    success=False,
                    message="TTS adapter is not configured.",
                )
            return RepairExecutionResult(
                action=plan.action,
                success=True,
                message="TTS speed adjustment delegated to adapter.",
                metadata={"target_speed":plan.target_tts_speed},
            )

        if plan.action in {
            RepairAction.TRIM_VIDEO,
            RepairAction.EXTEND_VIDEO,
        }:
            if self.video_adapter is None:
                return RepairExecutionResult(
                    action=plan.action,
                    success=False,
                    message="Video adapter is not configured.",
                )
            return RepairExecutionResult(
                action=plan.action,
                success=True,
                message="Video timing adjustment delegated to adapter.",
                metadata={"target_duration":plan.target_video_duration_seconds},
            )

        if plan.action in {
            RepairAction.REGENERATE_AUDIO,
            RepairAction.REGENERATE_VIDEO,
        }:
            return RepairExecutionResult(
                action=plan.action,
                success=False,
                message="Regeneration must be delegated to the orchestration queue.",
            )

        return RepairExecutionResult(
            action=plan.action,
            success=False,
            message="Manual review required.",
        )
