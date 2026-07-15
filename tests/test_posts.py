import importlib
import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(monkeypatch, tmp_path):
    db_path = tmp_path / "test_tripcast.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    import app.config as config_module
    import app.database as database_module
    import app.models.post as post_model_module
    import app.schemas.post as post_schema_module
    import app.services.post_service as post_service_module
    import app.routers.posts as posts_router_module
    import app.main as main_module

    for module in [
        config_module,
        database_module,
        post_model_module,
        post_schema_module,
        post_service_module,
        posts_router_module,
        main_module,
    ]:
        importlib.reload(module)

    with TestClient(main_module.app) as test_client:
        yield test_client


def test_create_read_update_and_verify_password(client):
    create_response = client.post(
        "/api/posts",
        json={
            "title": "테스트 제목",
            "content": "테스트 내용",
            "password": "1234",
            "category": "community",
        },
    )
    assert create_response.status_code == 201
    created_post = create_response.json()
    assert created_post["title"] == "테스트 제목"
    assert created_post["content"] == "테스트 내용"

    post_id = created_post["id"]

    list_response = client.get("/api/posts")
    assert list_response.status_code == 200
    posts = list_response.json()
    assert any(post["id"] == post_id for post in posts)

    update_response = client.put(
        f"/api/posts/{post_id}",
        json={
            "title": "수정된 제목",
            "content": "수정된 내용",
            "password": "5678",
            "category": "travel",
        },
    )
    assert update_response.status_code == 200
    updated_post = update_response.json()
    assert updated_post["title"] == "수정된 제목"
    assert updated_post["content"] == "수정된 내용"

    verify_response = client.post(
        f"/api/posts/{post_id}/verify-password",
        json={"password": "5678"},
    )
    assert verify_response.status_code == 200
    assert verify_response.json()["valid"] is True


def test_delete_post_requires_correct_password(client):
    create_response = client.post(
        "/api/posts",
        json={
            "title": "삭제 테스트",
            "content": "삭제용 내용",
            "password": "abcd",
            "category": "food",
        },
    )
    assert create_response.status_code == 201
    post_id = create_response.json()["id"]

    wrong_password_response = client.request(
        "DELETE",
        f"/api/posts/{post_id}",
        json={"password": "wrong"},
    )
    assert wrong_password_response.status_code == 403

    delete_response = client.request(
        "DELETE",
        f"/api/posts/{post_id}",
        json={"password": "abcd"},
    )
    assert delete_response.status_code == 204
