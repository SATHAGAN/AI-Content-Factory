from __future__ import annotations

import time

from app.services.benchmark.models import (
    BenchmarkConfig,
    BenchmarkResult,
    BenchmarkSample,
)


class BenchmarkRunner:
    """Provider-neutral inference benchmark harness.

    The runner intentionally measures the provider supplied to it; it does not
    assume a particular model library or GPU runtime.
    """

    def __init__(self, provider):
        self.provider=provider

    def _run_once(self, config: BenchmarkConfig):
        return self.provider.generate(
            prompt=config.prompt,
            width=config.width,
            height=config.height,
            frames=config.frames,
            fps=config.fps,
            metadata=config.metadata,
        )

    def run(self, config: BenchmarkConfig) -> BenchmarkResult:
        for _ in range(config.warmup_runs):
            self._run_once(config)

        result=BenchmarkResult(config)
        for run in range(1,config.measured_runs+1):
            start=time.perf_counter()
            try:
                self._run_once(config)
                elapsed=time.perf_counter()-start
                result.samples.append(BenchmarkSample(run,elapsed,True))
            except Exception as exc:
                elapsed=time.perf_counter()-start
                result.samples.append(
                    BenchmarkSample(run,elapsed,False,str(exc))
                )
        return result
