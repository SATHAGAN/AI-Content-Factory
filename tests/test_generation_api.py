def test_generation_endpoint_enqueues_scene_job(client):
    register = client.post(
        "/api/v1/auth/register",
        json={
            "email": "gen@example.com",
            "password": "StrongPass123!",
            "organization_name": "Generation Org",
        },
    )
    token = register.json()["access_token"]

    response = client.post(
        "/api/v1/generation/scene",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "scene": {
                "number": 1,
                "visual_prompt": "A small robot exploring a colorful garden",
                "narration": "The robot discovered a new world.",
            },
            "frames": 16,
            "fps": 16,
        },
    )
    assert response.status_code == 202
    assert response.json()["job_type"] == "generate_scene"
