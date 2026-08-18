def test_content_plan_endpoint(client):
    register = client.post(
        "/api/v1/auth/register",
        json={
            "email": "content@example.com",
            "password": "StrongPass123!",
            "organization_name": "Content",
        },
    )
    token = register.json()["access_token"]

    response = client.post(
        "/api/v1/content/plan",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "source_text": "A small fox learns to ask for help.",
            "content_category": "kids story",
            "language": "en",
            "audience": "children",
            "tone": "warm",
            "duration_seconds": 24,
            "video_type": "short",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"]
    assert data["scenes"]
    assert data["style_bible"]
