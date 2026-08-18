from pathlib import Path
from app.services.visuals.interface import VisualProvider
from app.services.visuals.models import VisualRequest, VisualResult

class MockVisualProvider(VisualProvider):
    def __init__(self, output_root="artifacts/visuals"):
        self.output_root=Path(output_root); self.output_root.mkdir(parents=True,exist_ok=True)

    def list_models(self):
        return [{"model_id":"mock-visual-v1","provider":"mock","enabled":True,
                 "kinds":["image","video"],"max_duration_seconds":60}]

    def generate(self, request):
        if not self.supports(request): raise ValueError("Unsupported visual request")
        out=self.output_root/request.job_id/request.scene_id
        out.mkdir(parents=True,exist_ok=True)
        ext=".png" if request.kind.value=="image" else ".mp4"
        path=out/f"visual{ext}"
        path.write_text(
            f"MOCK_VISUAL\nkind={request.kind.value}\nmodel={request.model or 'mock-visual-v1'}\n"
            f"prompt={request.prompt}\nduration={request.duration_seconds}\n",
            encoding="utf-8")
        return VisualResult(request.job_id,request.scene_id,"mock",
            request.model or "mock-visual-v1",request.kind,str(path),
            request.duration_seconds,request.width,request.height,{"mock":True})
