from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_home_page():
    r = client.get("/")
    assert r.status_code == 200
    assert "NetAutomate" in r.text
