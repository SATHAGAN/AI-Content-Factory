from app.services.channels.sample_channels import sample_channels


def test_multiple_channels_have_independent_config():
    channels=sample_channels()
    assert len(channels)==2
    assert channels[0].channel_id != channels[1].channel_id
    assert channels[0].voice.profile_id != channels[1].voice.profile_id
