def register(client, email, org):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "StrongPass123!",
            "organization_name": org,
        },
    )
    assert response.status_code == 201
    return response.json()["access_token"]


def test_register_login_and_me(client):
    token = register(client, "a@example.com", "Org A")

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "a@example.com"

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "a@example.com", "password": "StrongPass123!"},
    )
    assert login.status_code == 200


def test_channel_isolation(client):
    token_a = register(client, "a@example.com", "Org A")
    token_b = register(client, "b@example.com", "Org B")

    create = client.post(
        "/api/v1/channels",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"name": "A Channel", "daily_shorts_target": 5, "daily_long_target": 2},
    )
    assert create.status_code == 201

    channels_b = client.get(
        "/api/v1/channels",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert channels_b.status_code == 200
    assert channels_b.json() == []
