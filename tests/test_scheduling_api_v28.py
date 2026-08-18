def _register(client):
    response = client.post('/api/v1/auth/register', json={
        'email': 'scheduler@example.com',
        'password': 'StrongPass123!',
        'organization_name': 'Scheduler API Org',
    })
    assert response.status_code == 201
    return response.json()['access_token']


def test_run_daily_api_creates_configured_channel_jobs(client):
    token = _register(client)
    headers = {'Authorization': f'Bearer {token}'}

    channel = client.post('/api/v1/channels', headers=headers, json={
        'name': 'Kids Daily',
        'default_language': 'en',
        'daily_shorts_target': 3,
        'daily_long_target': 1,
    })
    assert channel.status_code == 201
    channel_id = channel.json()['id']

    response = client.post('/api/v1/scheduling/run-daily', headers=headers, json={
        'channel_id': channel_id,
        'day': '2026-08-17',
    })
    assert response.status_code == 200
    body = response.json()
    assert body['count'] == 4
    assert sum(x['content_format'] == 'short' for x in body['created_or_existing']) == 3
    assert sum(x['content_format'] == 'long' for x in body['created_or_existing']) == 1

    again = client.post('/api/v1/scheduling/run-daily', headers=headers, json={
        'channel_id': channel_id,
        'day': '2026-08-17',
    })
    assert again.status_code == 200
    assert {x['job_id'] for x in again.json()['created_or_existing']} == {
        x['job_id'] for x in body['created_or_existing']
    }
