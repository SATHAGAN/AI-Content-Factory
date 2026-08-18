from app.services.subtitles.srt import SubtitleLine, build_srt


def test_build_srt():
    text = build_srt([
        SubtitleLine(1, 0, 2.5, "Hello world"),
        SubtitleLine(2, 2.5, 5, "Second line"),
    ])
    assert "00:00:00,000 --> 00:00:02,500" in text
    assert "Hello world" in text
    assert text.count("\n\n") == 1
