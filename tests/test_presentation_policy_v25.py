from pathlib import Path

from app.services.presentation.branding import BrandProfile,BrandingPolicy
from app.services.presentation.music import MusicPolicy


def test_brand_profile_requires_name():
    try:
        BrandingPolicy().validate(BrandProfile(""))
    except ValueError:
        pass
    else:
        raise AssertionError("Expected validation error")


def test_music_policy_disabled_does_not_require_file():
    result=MusicPolicy().choose("kids",False,None)
    assert result["enabled"] is False


def test_music_policy_checks_path(tmp_path):
    music=tmp_path/"music.mp3"
    music.write_bytes(b"fake")
    result=MusicPolicy().choose("kids",True,str(music))
    assert result["enabled"] is True
    assert result["volume"]==0.10
