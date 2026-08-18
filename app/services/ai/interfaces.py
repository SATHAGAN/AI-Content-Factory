from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GenerationResult:
    provider: str
    model_id: str
    output: dict[str, Any]


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> GenerationResult:
        raise NotImplementedError


class VideoProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> GenerationResult:
        raise NotImplementedError


class TTSProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str, **kwargs: Any) -> GenerationResult:
        raise NotImplementedError
