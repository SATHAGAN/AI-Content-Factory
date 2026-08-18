def test_quality_api(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "judge@example.com",
            "password": "StrongPass123!",
            "organization_name": "Judge Org",
        },
    )
    token = response.json()["access_token"]

    response = client.post(
        "/api/v1/quality/judge",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "source_text": "A friendly fox learns kindness.",
            "narration": "The fox helped a bird.",
            "scene_prompt": "A friendly fox helps a small bird.",
            "image_description": "A forest with a fox and bird.",
            "media_qa_passed": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["decision"]["action"] == "approve"
    assert body["safety"]["passed"] is True
