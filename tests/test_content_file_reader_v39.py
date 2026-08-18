from pathlib import Path
import pytest

from app.services.content_source.file_reader import read_text_file


def test_text_file_reader(tmp_path):
    p=tmp_path/"story.txt"
    p.write_text("A story about a friendly robot.",encoding="utf-8")
    assert "friendly robot" in read_text_file(str(p))


def test_file_reader_rejects_unsupported_extension(tmp_path):
    p=tmp_path/"image.png"
    p.write_bytes(b"not really an image")
    with pytest.raises(ValueError):
        read_text_file(str(p))
