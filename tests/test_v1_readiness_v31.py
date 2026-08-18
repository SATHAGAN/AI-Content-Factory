from app.services.e2e.readiness import ReadinessCheck,V1Readiness
from app.services.e2e.contract import validate_production_result


def test_v1_readiness_fails_when_a_blocker_exists():
    result=V1Readiness().evaluate([
        ReadinessCheck("unit_tests",True),
        ReadinessCheck("real_model_inference",False,"GPU inference worker not configured"),
    ])
    assert result["ready"] is False
    assert result["failed"]==1


def test_v1_readiness_passes_when_all_checks_pass():
    result=V1Readiness().evaluate([
        ReadinessCheck("unit_tests",True),
        ReadinessCheck("storage",True),
        ReadinessCheck("publishing",True),
    ])
    assert result["ready"] is True
    assert result["failed"]==0


def test_production_contract_requires_all_stages():
    errors=validate_production_result({
        "status":"completed",
        "stages":["planning","media_generation","quality_assurance","finalization","publishing"],
        "outputs":{"final":{"video_path":"final.mp4"}},
    })
    assert errors==[]


def test_production_contract_rejects_incomplete_result():
    errors=validate_production_result({
        "status":"failed",
        "stages":["planning"],
        "outputs":{},
    })
    assert errors
