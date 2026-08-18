from app.services.quality.decision import QualityGate


def test_quality_gate_approve():
    decision = QualityGate().decide(True, 0.9, True)
    assert decision.action == "approve"


def test_quality_gate_regenerate_for_low_score():
    decision = QualityGate().decide(True, 0.5, True)
    assert decision.action == "regenerate"


def test_quality_gate_regenerate_for_media_failure():
    decision = QualityGate().decide(False, 0.9, True)
    assert decision.action == "regenerate"


def test_quality_gate_blocks_safety_failure():
    decision = QualityGate().decide(True, 0.99, False)
    assert decision.action == "block"
