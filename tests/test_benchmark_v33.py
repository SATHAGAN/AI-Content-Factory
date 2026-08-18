from app.services.benchmark.models import BenchmarkConfig
from app.services.benchmark.runner import BenchmarkRunner
from app.services.benchmark.synthetic_provider import SyntheticInferenceProvider


def test_benchmark_runner_measures_provider():
    result=BenchmarkRunner(
        SyntheticInferenceProvider(latency_seconds=0.001)
    ).run(BenchmarkConfig(
        name="synthetic",
        task="video",
        model_id="fake",
        prompt="test",
        warmup_runs=1,
        measured_runs=3,
    ))
    assert len(result.samples)==3
    assert result.success_rate==1.0
    assert result.average_seconds is not None
    assert result.average_seconds > 0


def test_benchmark_can_record_provider_failure():
    class Failing:
        def generate(self,**kwargs):
            raise RuntimeError("OOM")

    result=BenchmarkRunner(Failing()).run(BenchmarkConfig(
        name="failure",
        task="video",
        model_id="fake",
        prompt="test",
        warmup_runs=0,
        measured_runs=1,
    ))
    assert result.success_rate==0.0
    assert result.samples[0].error=="OOM"
