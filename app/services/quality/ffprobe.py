from __future__ import annotations
import json, shutil, subprocess
from app.services.quality.models import MediaProbe


class FFprobeAdapter:
    def __init__(self, executable: str = "ffprobe"):
        self.executable=executable

    def available(self) -> bool:
        return shutil.which(self.executable) is not None

    def probe(self, path: str) -> MediaProbe:
        if not self.available():
            raise RuntimeError("FFprobe is not installed or not available on PATH")
        result=subprocess.run([
            self.executable,"-v","error","-show_streams","-show_format",
            "-of","json",path
        ],capture_output=True,text=True,timeout=120)
        if result.returncode != 0:
            raise RuntimeError(result.stderr[-3000:] or "FFprobe failed")
        data=json.loads(result.stdout)
        streams=data.get("streams",[])
        video=next((s for s in streams if s.get("codec_type")=="video"),None)
        audio=next((s for s in streams if s.get("codec_type")=="audio"),None)
        duration=float(data.get("format",{}).get("duration") or 0)
        fps=None
        if video:
            raw=video.get("avg_frame_rate","0/1")
            try:
                n,d=raw.split("/")
                fps=float(n)/float(d) if float(d) else None
            except Exception:
                fps=None
        return MediaProbe(
            path=path,duration_seconds=duration,
            width=video.get("width") if video else None,
            height=video.get("height") if video else None,
            fps=fps,has_video=bool(video),has_audio=bool(audio),
        )
