from __future__ import annotations
import os
from app.services.judge.mock_judge import MockMultimodalJudge


def get_judge():
    provider=os.getenv("JUDGE_PROVIDER","mock")
    if provider=="mock":
        return MockMultimodalJudge()
    raise ValueError(f"Unsupported JUDGE_PROVIDER: {provider}")
