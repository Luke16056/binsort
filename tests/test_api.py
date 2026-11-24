import io

import pytest

from binsort.api import create_app
from binsort.item_detector import FakeDetector


@pytest.fixture
def client(tmp_path):
    return create_app(detector=FakeDetector(), db_path=tmp_path / "api.db").test_client()


def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"BinSort" in response.data


def test_post_photo(client, photo):
    response = client.post("/sort", data={"photo": (io.BytesIO(photo), "pile.jpg")},
                           content_type="multipart/form-data")
    assert response.status_code == 200
    assert len(response.get_json()["items"]) == 6


def test_post_text(client):
    response = client.post("/sort", data={"text": "banana peel"})
    assert response.get_json()["items"][0]["bin"] == "Food/organic"


def test_bad_file_gives_clear_error(client):
    response = client.post("/sort", data={"photo": (io.BytesIO(b"hello"), "notes.txt")},
                           content_type="multipart/form-data")
    assert response.status_code == 400
    assert "not a photo" in response.get_json()["error"]


def test_ai_down_still_returns_200(tmp_path, photo):
    client = create_app(detector=FakeDetector(fail=True), db_path=tmp_path / "api.db").test_client()
    response = client.post("/sort", data={"photo": (io.BytesIO(photo), "pile.jpg")},
                           content_type="multipart/form-data")
    assert response.status_code == 200
    assert response.get_json()["ai_down"] is True


def test_feedback_endpoint(client):
    response = client.post("/feedback", json={"result": {"name": "Can", "bin": "Recycling"}, "ok": True})
    assert response.get_json() == {"saved": True}


def test_feedback_without_result_is_400(client):
    assert client.post("/feedback", json={"ok": True}).status_code == 400
