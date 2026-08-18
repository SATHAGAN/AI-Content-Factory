def test_job_api_is_tenant_scoped(client):
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

    created = client.post(
        "/api/v1/jobs",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"job_type": "scene_generation", "payload": {"scene": 4}, "priority": 10},
    )
    assert created.status_code == 202
    job_id = created.json()["id"]

    own = client.get(f"/api/v1/jobs/{job_id}", headers={"Authorization": f"Bearer {token_a}"})
    assert own.status_code == 200

    foreign = client.get(f"/api/v1/jobs/{job_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert foreign.status_code == 404
