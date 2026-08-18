from __future__ import annotations


REQUIRED_STAGES=(
    "planning",
    "media_generation",
    "quality_assurance",
    "finalization",
    "publishing",
)


def validate_production_result(result: dict) -> list[str]:
    errors=[]
    if result.get("status")!="completed":
        errors.append("Production job did not complete")
    stages=result.get("stages",[])
    missing=[stage for stage in REQUIRED_STAGES if stage not in stages]
    if missing:
        errors.append("Missing stages: "+", ".join(missing))
    if not result.get("outputs",{}).get("final"):
        errors.append("Final output is missing")
    return errors
