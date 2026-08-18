from pathlib import Path

from app.services.timeline.models import SceneClip
from app.services.timeline.ffmpeg import (
    write_concat_manifest,
    build_concat_command,
    build_copy_concat_command,
)
from app.services.timeline.merge_service import TimelineMergeService


def test_manifest_and_commands(tmp_path):
    p1=tmp_path/"a.mp4"; p2=tmp_path/"b.mp4"
    p1.write_bytes(b"a"); p2.write_bytes(b"b")
    clips=[
        SceneClip("a",str(p1),2,metadata={"sequence":1}),
        SceneClip("b",str(p2),3,metadata={"sequence":2}),
    ]
    manifest=write_concat_manifest(clips,str(tmp_path/"concat.txt"))
    text=Path(manifest).read_text()
    assert "a.mp4" in text and "b.mp4" in text

    cmd=build_concat_command(manifest,str(tmp_path/"final.mp4"))
    assert cmd[:6]==["ffmpeg","-y","-f","concat","-safe","0"]
    assert "libx264" in cmd

    copy_cmd=build_copy_concat_command(manifest,str(tmp_path/"copy.mp4"))
    assert "-c" in copy_cmd and "copy" in copy_cmd


def test_merge_service_prepares_and_runs(tmp_path):
    p=tmp_path/"a.mp4"; p.write_bytes(b"a")
    calls=[]
    service=TimelineMergeService(lambda command:calls.append(command))
    result=service.merge(
        [SceneClip("a",str(p),2,metadata={"sequence":1})],
        str(tmp_path/"concat.txt"),
        str(tmp_path/"final.mp4"),
    )
    assert calls
    assert result["timeline"].total_duration_seconds==2
