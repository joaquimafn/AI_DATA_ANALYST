"""Unit tests for API endpoints"""


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "AI Data Analyst API"
    assert "version" in data


def test_health_endpoint_degraded(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "redis" in data


def test_query_endpoint_placeholder(client):
    response = client.post("/api/v1/query", json={"question": "What are the top selling products?"})
    assert response.status_code == 200
    data = response.json()
    assert "sql" in data
    assert "explanation" in data
    assert data["cached"] is False


def test_query_endpoint_validation_error(client):
    response = client.post("/api/v1/query", json={"question": "Hi"})
    assert response.status_code == 422


def test_query_endpoint_missing_question(client):
    response = client.post("/api/v1/query", json={})
    assert response.status_code == 422
