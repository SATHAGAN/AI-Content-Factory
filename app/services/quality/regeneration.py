from __future__ import annotations
from app.services.quality.models import QAReport


REGENERATE_CODES={"missing_video","missing_audio","duration_mismatch"}


def regeneration_plan(report: QAReport) -> dict:
    scenes=sorted({
        issue.scene_number for issue in report.issues
        if issue.scene_number is not None and issue.code in REGENERATE_CODES
    })
    return {
        "required":bool(scenes),
        "scene_numbers":scenes,
        "reason_codes":sorted({
            issue.code for issue in report.issues if issue.code in REGENERATE_CODES
        }),
    }
