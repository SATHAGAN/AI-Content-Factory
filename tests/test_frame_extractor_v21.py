from app.services.vlm.frame_extractor import FrameExtractor


def test_frame_extractor_rejects_bad_parameters():
    extractor=FrameExtractor()
    try:
        extractor.extract("video.mp4","frames",fps=0)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected fps validation")

    try:
        extractor.extract("video.mp4","frames",max_frames=0)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected max_frames validation")
