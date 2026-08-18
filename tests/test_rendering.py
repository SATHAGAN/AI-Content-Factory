from pathlib import Path

from app.services.rendering.assembly import VideoAssemblyService
from app.services.rendering.pipeline import FinalRenderPipeline


class FakeFFmpeg:
    def __init__(self):
        self.calls=[]

    def run(self,args,timeout=1800):
        self.calls.append(args)


def test_concat_manifest_is_created(tmp_path):
    ff=FakeFFmpeg()
    service=VideoAssemblyService(ff)
    result=service.build_concat_file(["a.mp4","b.mp4"],str(tmp_path))
    text=Path(result).read_text()
    assert "a.mp4" in text
    assert "b.mp4" in text


def test_final_pipeline_assembles_ordered_scenes(tmp_path):
    class FakeAssembler:
        def assemble(self, paths, output):
            assert paths==["one.mp4","two.mp4"]
            Path(output).write_bytes(b"video")
            return output

    pipeline=FinalRenderPipeline(assembler=FakeAssembler())
    result=pipeline.render([
        {"number":2,"video_path":"two.mp4","audio_path":None},
        {"number":1,"video_path":"one.mp4","audio_path":None},
    ],str(tmp_path))
    assert result["scene_count"]==2
    assert result["status"]=="rendered"


def test_multiple_scene_audio_is_not_silently_dropped(tmp_path):
    class FakeAssembler:
        def assemble(self, paths, output):
            Path(output).write_bytes(b"video")
            return output
    pipeline=FinalRenderPipeline(assembler=FakeAssembler())
    try:
        pipeline.render([
            {"number":1,"video_path":"one.mp4","audio_path":"one.wav"},
            {"number":2,"video_path":"two.mp4","audio_path":"two.wav"},
        ],str(tmp_path))
    except RuntimeError as exc:
        assert "Multiple scene audio tracks" in str(exc)
    else:
        raise AssertionError("Expected multi-track audio guard")
