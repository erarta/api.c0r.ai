import os
from importlib import reload
from fastapi.testclient import TestClient


def make_image_bytes():
    # Tiny 1x1 transparent PNG (fixed bytes)
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDATx\x9cc``\x00\x00\x00\x02\x00\x01\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82"
    )


def test_label_analyze_requires_auth(monkeypatch):
    # Set token before import
    monkeypatch.setenv("INTERNAL_API_TOKEN", "x" * 40)

    from services.ml import main as ml_main
    reload(ml_main)

    client = TestClient(ml_main.app)
    files = {"photo": ("test.png", make_image_bytes(), "image/png")}
    resp = client.post("/api/v1/label/analyze", files=files)
    assert resp.status_code == 401


def test_label_analyze_skeleton_ok(monkeypatch):
    monkeypatch.setenv("INTERNAL_API_TOKEN", "y" * 40)
    from services.ml import main as ml_main
    reload(ml_main)

    client = TestClient(ml_main.app)
    files = {"photo": ("test.png", make_image_bytes(), "image/png")}
    headers = {"X-Internal-Token": "y" * 40}
    resp = client.post("/api/v1/label/analyze", files=files, data={"user_language": "en"}, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["language"] == "en"
    assert isinstance(data["barcodes"], list)
    assert data["ocr_text"] == ""
