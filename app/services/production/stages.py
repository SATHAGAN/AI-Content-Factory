from __future__ import annotations


class PlannerStage:
    def __init__(self, planner):
        self.planner=planner

    def plan(self, *args, **kwargs):
        return self.planner.plan(*args, **kwargs)


class MediaStage:
    def __init__(self, generator):
        self.generator=generator

    def generate(self, plan, job):
        return self.generator.generate(plan,job)


class QAStage:
    def __init__(self, evaluator):
        self.evaluator=evaluator

    def evaluate(self, plan, scenes, job):
        return self.evaluator.evaluate(plan,scenes,job)


class FinalizationStage:
    def __init__(self, finalizer):
        self.finalizer=finalizer

    def render(self, plan, scenes, job):
        return self.finalizer.render(plan,scenes,job)


class PublishingStage:
    def __init__(self, publisher):
        self.publisher=publisher

    def publish(self, final, job):
        return self.publisher.publish(final,job)
