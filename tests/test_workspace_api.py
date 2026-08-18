def test_workspace_create_and_enqueue(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "workspace@example.com",
            "password": "StrongPass123!",
            "organization_name": "Workspace Org",
        },
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    project = client.post(
        "/api/v1/workspace/projects",
        headers=headers,
        json={
            "name": "Fox Story",
            "category": "Kids",
            "format": "long",
            "duration_seconds": 300,
            "source_text": "A fox learns to ask for help.",
            "channel_ids": ["kids", "facts"],
        },
    )
    assert project.status_code == 201
    project_id = project.json()["id"]

    job = client.post(
        "/api/v1/workspace/generate",
        headers=headers,
        json={"project_id": project_id},
    )
    assert job.status_code == 202
    assert job.json()["status"] == "queued"

    jobs = client.get("/api/v1/workspace/jobs", headers=headers)
    assert jobs.status_code == 200
    assert len(jobs.json()) == 1


def test_workspace_isolation(client):
    a = client.post(
        "/api/v1/auth/register",
        json={"email":"a-isolation@example.com","password":"StrongPass123!","organization_name":"Org A"},
    ).json()["access_token"]
    b = client.post(
        "/api/v1/auth/register",
        json={"email":"b-isolation@example.com","password":"StrongPass123!","organization_name":"Org B"},
    ).json()["access_token"]

    created = client.post(
        "/api/v1/workspace/projects",
        headers={"Authorization":f"Bearer {a}"},
        json={"name":"Private","source_text":"private source"},
    ).json()

    response = client.get(
        f"/api/v1/workspace/projects/{created['id']}",
        headers={"Authorization":f"Bearer {b}"},
    )
    assert response.status_code == 404
