from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class BenchmarkConfig:
    name: str
    task: str
    model_id: str
    prompt: str
    width: int = 512
    height: int = 512
    frames: int = 16
    fps: int = 8
    warmup_runs: int = 1
    measured_runs: int = 3
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class BenchmarkSample:
    run: int
    elapsed_seconds: float
    success: bool
    error: str | None = None


@dataclass
class BenchmarkResult:
    config: BenchmarkConfig
    samples: list[BenchmarkSample] = field(default_factory=list)

    @property
    def successful_samples(self):
        return [s for s in self.samples if s.success]

    @property
    def average_seconds(self):
        values=[s.elapsed_seconds for s in self.successful_samples]
        return sum(values)/len(values) if values else None

    @property
    def success_rate(self):
        return len(self.successful_samples)/len(self.samples) if self.samples else 0.0

    def to_dict(self):
        return {
            "config":self.config.__dict__,
            "samples":[s.__dict__ for s in self.samples],
            "average_seconds":self.average_seconds,
            "success_rate":self.success_rate,
        }
