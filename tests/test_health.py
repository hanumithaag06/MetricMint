def test_health_is_fast_and_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "app": "metric-mint", "environment": "local"}


def test_ready_without_database(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["database"] == "not configured"
