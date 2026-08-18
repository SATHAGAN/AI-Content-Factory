def test_source_types_are_extensible(client):
    register = client.post(
        "/api/v1/auth/register",
        json={
            "email": "source@example.com",
            "password": "StrongPass123!",
            "organization_name": "Sources",
        },
    )
    token = register.json()["access_token"]

    response = client.post(
        "/api/v1/sources",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "source_type": "transcript",
            "title": "Sample transcript",
            "content_text": "A sample source.",
        },
    )
    assert response.status_code == 201
    assert response.json()["source_type"] == "transcript"
