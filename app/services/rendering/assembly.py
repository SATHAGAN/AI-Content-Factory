from __future__ import annotations

from pathlib import Path
from app.services.rendering.ffmpeg_adapter import FFmpegAdapter


class VideoAssemblyService:
    """Assemble generated scene videos into a single long-form video.

    The service supports a deterministic concat workflow and deliberately
    keeps FFmpeg behind a small adapter for testability.
    """

    def __init__(self, ffmpeg: FFmpegAdapter | None = None):
        self.ffmpeg = ffmpeg or FFmpegAdapter()

    def build_concat_file(self, video_paths: list[str], output_dir: str) -> str:
        if not video_paths:
            raise ValueError("At least one video is required")
        directory=Path(output_dir)
        directory.mkdir(parents=True,exist_ok=True)
        list_file=directory/"concat.txt"
        lines=[]
        for path in video_paths:
            safe=Path(path).resolve()
            lines.append(f"file '{str(safe).replace(chr(39), chr(39)+chr(92)+chr(39)+chr(39))}'")
        list_file.write_text("\n".join(lines)+"\n",encoding="utf-8")
        return str(list_file)

    def assemble(self, video_paths: list[str], output_path: str) -> str:
        output=Path(output_path)
        output.parent.mkdir(parents=True,exist_ok=True)
        list_file=self.build_concat_file(video_paths,str(output.parent))
        self.ffmpeg.run(["-f","concat","-safe","0","-i",list_file,"-c","copy",str(output)])
        return str(output)
