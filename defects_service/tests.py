from fastapi.testclient import TestClient

from defects_service.main import app
from defects_service.schemas import DefectCreate, DefectUpdate, StatusUpdate, CommentCreate, AttachmentsAdd

client = TestClient(app)


def test_create_defect():
    payload = DefectCreate(
        title="New Defect",
        desc="Description of defect",
        priority="Высокий",
        assignee="Developer",
        due="2025-12-31"
    )
    response = client.post("http://localhost:8080/defects_service/defects", json=payload.model_dump())
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload.title
    assert data["priority"] == payload.priority
    created_defect_id = data["id"]
    return created_defect_id


def test_get_defect():
    defect_id = test_create_defect()
    response = client.get(f"http://localhost:8080/defects_service/defects/{defect_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == defect_id
    assert data["title"] == "New Defect"


def test_update_defect():
    defect_id = test_create_defect()
    payload = DefectUpdate(title="Updated Title", status="В процессе", priority="Средний", assignee="Developer")
    response = client.patch(f"http://localhost:8080/defects_service/defects/{defect_id}", json=payload.model_dump())
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["status"] == "В процессе"
    assert data["priority"] == "Средний"


def test_update_status():
    defect_id = test_create_defect()
    payload = StatusUpdate(status="Закрыта")
    response = client.patch(f"http://localhost:8080/defects_service/defects/{defect_id}/status", json=payload.model_dump())
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Закрыта"


def test_add_comment():
    defect_id = test_create_defect()
    payload = CommentCreate(text="New comment")
    response = client.post(f"http://localhost:8080/defects_service/defects/{defect_id}/comments", json=payload.model_dump())
    assert response.status_code == 200
    data = response.json()
    assert len(data["comments"]) > 0
    assert data["comments"][0]["text"] == payload.text


def test_add_attachments():
    defect_id = test_create_defect()
    files = [
        {"name": "attachment1.txt", "size": 1234, "content": "file content"},
        {"name": "attachment2.txt", "size": 5678, "content": "file content"}
    ]
    payload = AttachmentsAdd(files=files)
    response = client.post(f"http://localhost:8080/defects_service/defects/{defect_id}/attachments", json=payload.model_dump())
    assert response.status_code == 200
    data = response.json()
    assert len(data["attachments"]) == 2
    assert data["attachments"][0]["name"] == files[0]["name"]


def test_remove_attachment():
    defect_id = test_create_defect()
    files = [
        {"name": "attachment1.txt", "size": 1234, "content": "file content"},
        {"name": "attachment2.txt", "size": 5678, "content": "file content"}
    ]
    payload = AttachmentsAdd(files=files)
    response = client.post(f"http://localhost:8080/defects_service/defects/{defect_id}/attachments",
                           json=payload.model_dump())
    assert response.status_code == 200
    response = client.delete(f"http://localhost:8080/defects_service/defects/{defect_id}/attachments/attachment1.txt")
    assert response.status_code == 200
    data = response.json()
    assert len(data["attachments"]) == 1
    assert data["attachments"][0]["name"] == "attachment2.txt"


def test_delete_defect():
    defect_id = test_create_defect()
    response = client.delete(f"http://localhost:8080/defects_service/defects/{defect_id}")
    assert response.status_code == 204


def test_get_stats():
    response = client.get("http://localhost:8080/defects_service/defects/stats")
    assert response.status_code == 200
    data = response.json()
    total = data.get("total")
    closed = data.get("closed")
    assert total is not None, "Total defects count is missing"
    assert closed is not None, "Closed defects count is missing"
    print(f"Total defects: {total}, Closed defects: {closed}")
