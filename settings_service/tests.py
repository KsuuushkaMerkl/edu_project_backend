from fastapi.testclient import TestClient
from settings_service.main import app
from settings_service.schemas import StageOptionCreate

client = TestClient(app)


def test_add_stage_option():
    payload = StageOptionCreate(name="Тестовый этап")
    response = client.post("http://localhost:8080/settings_service/settings/stages", json=payload.model_dump())
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload.name
    return data["name"]


def test_list_stage_options():
    response = client.get("http://localhost:8080/settings_service/settings/stages")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["items"], list)
    assert len(data["items"]) > 0


def test_delete_stage_option():
    stage_name = test_add_stage_option()
    response = client.delete(f"http://localhost:8080/settings_service/settings/stages/{stage_name}")
    assert response.status_code == 204
    response = client.get("http://localhost:8080/settings_service/settings/stages")
    data = response.json()
    assert stage_name not in [item["name"] for item in data["items"]]


def test_reset_stage_options():
    response = client.post("http://localhost:8080/settings_service/settings/stages/reset")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3
    assert all(stage["name"] in ["Анализ", "В разработке", "Выполнено"] for stage in data["items"])


def test_add_stage_option_empty_name():
    payload = StageOptionCreate(name="")
    response = client.post("http://localhost:8080/settings_service/settings/stages", json=payload.model_dump())
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Имя этапа не может быть пустым"


def test_add_duplicate_stage_option():
    test_add_stage_option()
    payload = StageOptionCreate(name="Тестовый этап")
    response = client.post("http://localhost:8080/settings_service/settings/stages", json=payload.model_dump())
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload.name
