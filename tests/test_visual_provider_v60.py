from pathlib import Path
from app.services.visuals import VisualKind, VisualRequest, MockVisualProvider

def test_dynamic_visual_provider_generates_video(tmp_path):
    p=MockVisualProvider(tmp_path)
    r=p.generate(VisualRequest("job","scene-1","a colorful robot",5,width=1080,height=1920))
    assert r.kind==VisualKind.VIDEO and Path(r.output_path).is_file()
    assert "a colorful robot" in Path(r.output_path).read_text()

def test_dynamic_visual_provider_generates_image(tmp_path):
    p=MockVisualProvider(tmp_path)
    r=p.generate(VisualRequest("job","scene-1","a tree",0,kind=VisualKind.IMAGE))
    assert r.kind==VisualKind.IMAGE and Path(r.output_path).suffix==".png"

def test_model_can_be_selected(tmp_path):
    p=MockVisualProvider(tmp_path)
    r=p.generate(VisualRequest("job","s","x",2,model="mock-visual-v1"))
    assert r.model=="mock-visual-v1"
