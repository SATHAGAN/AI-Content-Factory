from __future__ import annotations

from dataclasses import replace

from app.services.orchestration.models import (
    MediaState,
    OrchestrationPolicy,
    RepairRun,
    RepairRunStatus,
)
from app.services.repair.models import RepairAction, RepairRequest
from app.services.repair.planner import RepairPlanner
from app.services.sync.analyzer import AVSyncAnalyzer
from app.services.sync.models import SyncConfig


class MediaRepairOrchestrator:
    """Connects sync analysis, repair planning, media execution and re-checks."""

    def __init__(
        self,
        *,
        sync_analyzer: AVSyncAnalyzer | None = None,
        repair_planner: RepairPlanner | None = None,
        media_engine=None,
        policy: OrchestrationPolicy | None = None,
    ):
        self.sync_analyzer = sync_analyzer or AVSyncAnalyzer(
            SyncConfig(max_duration_delta_seconds=0.35)
        )
        self.repair_planner = repair_planner or RepairPlanner()
        self.media_engine = media_engine
        self.policy = policy or OrchestrationPolicy()

    def evaluate(self, state: MediaState, history: tuple[dict, ...] = ()) -> RepairRun:
        # Missing source media is never repairable by a timing-only operation.
        # Stop before the planner could interpret zero duration as a valid target.
        if state.audio_path is None or state.video_path is None:
            return RepairRun(
                status=RepairRunStatus.MANUAL_REVIEW,
                attempt=len(history),
                state=state,
                action="manual_review",
                message="Required audio or video artifact is missing.",
                history=history + ({
                    "event": "manual_review",
                    "reason": "missing_media_artifact",
                },),
            )

        report = self.sync_analyzer.analyze(
            audio_duration_seconds=state.audio_duration_seconds,
            video_duration_seconds=state.video_duration_seconds,
            audio_present=state.audio_path is not None,
            video_present=state.video_path is not None,
            metadata=state.metadata,
        )

        if report.passed:
            return RepairRun(
                status=RepairRunStatus.PASSED,
                attempt=len(history),
                state=state,
                action="continue",
                message="Media passed synchronization quality gate.",
                history=history + ({
                    "event": "sync_pass",
                    "delta_seconds": report.duration_delta_seconds,
                    "score": report.score,
                },),
            )

        if len(history) >= self.policy.max_attempts:
            return RepairRun(
                status=RepairRunStatus.MANUAL_REVIEW,
                attempt=len(history),
                state=state,
                action="manual_review",
                message="Maximum automatic repair attempts reached.",
                history=history + ({
                    "event": "manual_review",
                    "reason": "maximum_attempts",
                },),
            )

        plan = self.repair_planner.plan(RepairRequest(
            audio_duration_seconds=state.audio_duration_seconds,
            video_duration_seconds=state.video_duration_seconds,
            current_tts_speed=state.tts_speed,
            attempt=len(history),
            audio_regeneration_available=state.audio_path is not None,
            video_regeneration_available=state.video_path is not None,
        ))

        if plan.action == RepairAction.NONE:
            return RepairRun(
                status=RepairRunStatus.PASSED,
                attempt=len(history),
                state=state,
                action="continue",
                message="No repair required.",
                history=history,
            )

        if plan.action == RepairAction.MANUAL_REVIEW:
            return RepairRun(
                status=RepairRunStatus.MANUAL_REVIEW,
                attempt=len(history),
                state=state,
                action=plan.action.value,
                message=plan.reason,
                history=history + ({
                    "event": "manual_review",
                    "reason": plan.reason,
                },),
            )

        repaired = self._apply_simulated_timing_repair(state, plan.action, plan.target_tts_speed, plan.target_video_duration_seconds)
        event = {
            "event": "repair_applied",
            "action": plan.action.value,
            "attempt": len(history) + 1,
            "reason": plan.reason,
        }
        return RepairRun(
            status=RepairRunStatus.REPAIRING,
            attempt=len(history) + 1,
            state=repaired,
            action=plan.action.value,
            message="Repair planned and applied to orchestration state.",
            history=history + (event,),
        )

    def run_until_terminal(self, state: MediaState) -> RepairRun:
        history: tuple[dict, ...] = ()
        current = state

        for _ in range(self.policy.max_attempts + 1):
            result = self.evaluate(current, history)
            if result.status in {
                RepairRunStatus.PASSED,
                RepairRunStatus.MANUAL_REVIEW,
            }:
                return result

            current = result.state
            history = result.history

        return RepairRun(
            status=RepairRunStatus.MANUAL_REVIEW,
            attempt=len(history),
            state=current,
            action="manual_review",
            message="Safety stop reached.",
            history=history + ({"event": "manual_review", "reason": "safety_stop"},),
        )

    @staticmethod
    def _apply_simulated_timing_repair(
        state: MediaState,
        action: RepairAction,
        target_tts_speed: float | None,
        target_video_duration: float | None,
    ) -> MediaState:
        if action == RepairAction.ADJUST_TTS_SPEED and target_tts_speed:
            # Duration changes inversely with speech speed.
            new_audio = state.audio_duration_seconds * state.tts_speed / target_tts_speed
            return replace(
                state,
                audio_duration_seconds=round(new_audio, 6),
                tts_speed=target_tts_speed,
            )

        if action in {RepairAction.TRIM_VIDEO, RepairAction.EXTEND_VIDEO} and target_video_duration is not None:
            return replace(
                state,
                video_duration_seconds=round(target_video_duration, 6),
            )

        # Regeneration actions are intentionally represented as a no-op state
        # transition here; real providers are connected by later adapters.
        return state
