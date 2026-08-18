from abc import ABC, abstractmethod
from app.services.visuals.models import VisualRequest, VisualResult

class VisualProvider(ABC):
    @abstractmethod
    def list_models(self): raise NotImplementedError

    @abstractmethod
    def generate(self, request: VisualRequest) -> VisualResult: raise NotImplementedError

    def supports(self, request: VisualRequest) -> bool:
        return any(
            m["enabled"] and request.kind.value in m["kinds"]
            and (request.model is None or request.model == m["model_id"])
            and request.duration_seconds <= m["max_duration_seconds"]
            for m in self.list_models()
        )
