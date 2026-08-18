def test_project_requires_owned_references(client):
    a = client.post(
        "/api/v1/auth/register",
        json={"email": "a@example.com", "password": "StrongPass123!", "organization_name": "Org A"},
    )
    b = client.post(
        "/api/v1/auth/register",
        json={"email": "b@example.com", "password": "StrongPass123!", "organization_name": "Org B"},
    )
    token_a = a.json()["access_token"]
    token_b = b.json()["access_token"]

    channel = client.post(
        "/api/v1/channels",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"name": "A Channel"},
    )
    channel_id = channel.json()["id"]

    response = client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"name": "Illegal project", "channel_id": channel_id},
    )
    assert response.status_code == 404


def test_create_and_list_project(client):
    register = client.post(
        "/api/v1/auth/register",
        json={"email": "p@example.com", "password": "StrongPass123!", "organization_name": "Projects"},
    )
    token = register.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    profile = client.post(
        "/api/v1/content-profiles",
        headers=headers,
        json={"name": "Kids", "category": "kids"},
    )
    project = client.post(
        "/api/v1/projects",
        headers=headers,
        json={
            "name": "Dinosaur Adventure",
            "content_profile_id": profile.json()["id"],
            "settings": {"duration_seconds": 300, "video_type": "long"},
        },
    )
    assert project.status_code == 201
    assert project.json()["settings"]["duration_seconds"] == 300

    listed = client.get("/api/v1/projects", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1
