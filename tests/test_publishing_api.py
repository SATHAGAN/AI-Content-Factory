import os


def test_publish_api_with_mock_provider(client, monkeypatch):
    monkeypatch.setenv("PUBLISHER_PROVIDER", "mock")

    register = client.post(
        "/api/v1/auth/register",
        json={
            "email": "publish@example.com",
            "password": "StrongPass123!",
            "organization_name": "Publish Org",
        },
    )
    token = register.json()["access_token"]

    response = client.post(
        "/api/v1/publishing/publish",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "channel_id": "channel-1",
            "shorts_limit": 5,
            "long_limit": 2,
            "targets": [
                {
                    "platform": "youtube",
                    "media_uri": "/tmp/video.mp4",
                    "content_format": "short",
                    "title": "Test Short",
                },
                {
                    "platform": "instagram",
                    "media_uri": "/tmp/video.mp4",
                    "content_format": "short",
                    "caption": "Test caption",
                },
            ],
        },
    )
    assert response.status_code == 202
    body = response.json()
    assert len(body["published"]) == 2
    assert body["errors"] == []
