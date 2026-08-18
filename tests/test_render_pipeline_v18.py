from pathlib import Path

from app.services.rendering.pipeline import FinalRenderPipeline


def test_pipeline_handles_multiple_audio_tracks(tmp_path):
    class Assembler:
        def assemble(self, paths, output):
            Path(output).write_bytes(b"video")
            return output

    class TimelineRenderer:
        def render(self, timeline, output):
            Path(output).write_bytes(b"audio")
            return output

    class Audio:
        def mux(self, video, audio, output):
            Path(output).write_bytes(b"final")
            return output

        def add_background_music(self,*args,**kwargs):
            return args[2]

    pipeline=FinalRenderPipeline(
        assembler=Assembler(),
        narration_renderer=TimelineRenderer(),
        audio=Audio(),
    )
    result=pipeline.render([
        {"number":1,"video_path":"one.mp4","audio_path":"one.wav","video_duration_seconds":5,"audio_duration_seconds":5},
        {"number":2,"video_path":"two.mp4","audio_path":"two.wav","video_duration_seconds":5,"audio_duration_seconds":5},
    ],str(tmp_path))
    assert result["scene_count"]==2
    assert result["narration_duration_seconds"]==10
    assert result["sync_report"]["status"]=="pass"
