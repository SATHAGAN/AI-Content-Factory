def test_content_profile_is_dynamic(client):
    register = client.post(
        "/api/v1/auth/register",
        json={
            "email": "profile@example.com",
            "password": "StrongPass123!",
            "organization_name": "Profiles",
        },
    )
    token = register.json()["access_token"]

    response = client.post(
        "/api/v1/content-profiles",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Custom Dinosaur Stories",
            "category": "custom",
            "audience": "children 6-9",
            "language": "en",
            "tone": "adventurous",
            "settings": {"visual_style": "3d", "duration_seconds": 300},
        },
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Custom Dinosaur Stories"
    assert response.json()["settings"]["duration_seconds"] == 300
