from __future__ import annotations

from pathlib import Path


def write_concat_manifest(clips, manifest_path: str) -> str:
    """Create an FFmpeg concat-demuxer manifest using absolute normalized paths."""
    target=Path(manifest_path)
    target.parent.mkdir(parents=True,exist_ok=True)

    lines=[]
    for clip in clips:
        path=Path(clip.video_path).resolve()
        if not path.is_file():
            raise FileNotFoundError(str(path))
        safe=str(path).replace("'", r"'\''")
        lines.append(f"file '{safe}'")

    target.write_text("\n".join(lines)+"\n",encoding="utf-8")
    return str(target)


def build_concat_command(manifest_path: str, output_path: str) -> list[str]:
    return [
        "ffmpeg","-y",
        "-f","concat",
        "-safe","0",
        "-i",manifest_path,
        "-c:v","libx264",
        "-pix_fmt","yuv420p",
        "-c:a","aac",
        output_path,
    ]


def build_copy_concat_command(manifest_path: str, output_path: str) -> list[str]:
    """Fast path when all source clips have matching codecs/parameters."""
    return [
        "ffmpeg","-y",
        "-f","concat",
        "-safe","0",
        "-i",manifest_path,
        "-c","copy",
        output_path,
    ]
