from dataclasses import dataclass
@dataclass(frozen=True)
class VisualQAResult:
    passed: bool
    score: float
    reasons: tuple[str,...]=()
    retry_recommended: bool=False
