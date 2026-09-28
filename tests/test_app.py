from fastapi.testclient import TestClient

from app.main import app
from app.db import init_db


def test_health():

    init_db()

    client = TestClient(app)

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_home_page():

    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200

    assert "PocketSmart" in response.text


def test_login_page():

    client = TestClient(app)

    response = client.get("/login")

    assert response.status_code == 200

    assert "Welcome Back" in response.text


def test_protected_api():

    client = TestClient(app)

    response = client.post(
        "/api/recommendations/home",
        json={
            "total_budget": 50000,
            "num_lights": 4,
            "num_fans": 2,
            "num_furniture": 3,
            "num_dining_tables": 1,
            "has_living_room": True,
            "has_kitchen": False,
            "has_bedroom": False,
            "additional_requirements": ""
        }
    )

    assert response.status_code == 401