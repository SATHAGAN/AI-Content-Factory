def test_content_planning_endpoint(client):
    response=client.post(
        "/api/v1/content-planning/plan",
        json={
            "source_text":"A small fox finds a lost bird and helps it return home.",
            "category":"Kids",
            "language":"English",
            "duration_seconds":60,
            "tone":"Warm",
            "audience":"Children"
        }
    )
    assert response.status_code==200
    body=response.json()
    assert body["target_duration_seconds"]==60
    assert len(body["scenes"])>=1
    assert body["scenes"][0]["visual_prompt"]
    assert body["scenes"][0]["narration"]
