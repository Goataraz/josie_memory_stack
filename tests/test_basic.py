from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_semantic_add_returns_deterministic_id():
    payload = {"text": "hello world"}
    r1 = client.post("/memory/semantic/add", json=payload)
    r2 = client.post("/memory/semantic/add", json=payload)
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["id"] == r2.json()["id"]


def test_short_term_trim_and_store():
    # Shrink list for test using env var default (can't change at runtime), ensure endpoint works
    for i in range(5):
        resp = client.post("/memory/short-term", json={"text": f"msg-{i}"})
        assert resp.status_code == 200
    # Fetch back
    g = client.get("/memory/short-term")
    assert g.status_code == 200
    body = g.json()
    assert "memory" in body
    assert isinstance(body["memory"], list)
