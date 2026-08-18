from app.services.quality.models import MediaProbe
from app.services.quality.pipeline import MediaQAPipeline


class FakeProber:
    def probe(self,path):
        return MediaProbe(
            path=path,duration_seconds=5,width=720,height=1280,
            fps=24,has_video=True,has_audio=True
        )


def test_pipeline_probes_all_scenes():
    result=MediaQAPipeline(prober=FakeProber()).run([
        {"number":1,"video_path":"a.mp4","video_duration_seconds":5},
        {"number":2,"video_path":"b.mp4","video_duration_seconds":5},
    ])
    assert result["status"]=="pass"
    assert len(result["scene_reports"])==2
    assert result["regeneration"]["required"] is False
