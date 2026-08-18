from app.services.recovery.controller import SelfHealingController


class Generator:
    def __init__(self):
        self.calls=0

    def generate(self, scene):
        self.calls += 1
        return {"generated_version":self.calls}


class Evaluator:
    def __init__(self, pass_after=2):
        self.calls=0
        self.pass_after=pass_after

    def evaluate(self, scene):
        self.calls += 1
        if self.calls >= self.pass_after:
            return {
                "decision":"approve",
                "issues":[],
                "regeneration":{"reasons":[]},
            }
        return {
            "decision":"regenerate",
            "issues":[{"message":"Character inconsistency"}],
            "regeneration":{"reasons":["character_consistency"]},
        }


def test_failed_scene_is_regenerated_and_then_approved():
    controller=SelfHealingController(Generator(),Evaluator(pass_after=2),max_attempts=2)
    scene={"number":4,"visual_prompt":"A fox walks."}
    updated,attempts,ok=controller.recover_scene(scene)
    assert ok is True
    assert len(attempts)==1
    assert updated["regeneration_attempt"]==1
    assert "character" in updated["visual_prompt"].lower()


def test_recovery_is_bounded_and_goes_to_manual_review():
    controller=SelfHealingController(Generator(),Evaluator(pass_after=99),max_attempts=2)
    scene={"number":7,"visual_prompt":"A fox walks."}
    updated,attempts,ok=controller.recover_scene(scene)
    assert ok is False
    assert len(attempts)==2


def test_recovery_only_marks_failed_scenes_for_manual_review():
    controller=SelfHealingController(Generator(),Evaluator(pass_after=99),max_attempts=1)
    result=controller.recover([
        {"number":1,"visual_prompt":"one"},
        {"number":2,"visual_prompt":"two"},
    ])
    assert result.status=="failed"
    assert result.manual_review_scenes==[1,2]
