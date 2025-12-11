import pytest
from fastapi.testclient import TestClient
from projects_service.main import app
from projects_service.schemas import ProjectCreate, ProjectUpdate, StageAdd, AttachmentsAdd

client = TestClient(app)

def test_create_project():
    payload = ProjectCreate(
        name="New Project",
        description="Description of the new project"
    )

    response = client.post("http://localhost:8080/projects_service/projects", json=payload.model_dump())

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload.name
    assert data["description"] == payload.description
    return data["id"]


def test_get_project():
    project_id = test_create_project()
    response = client.get(f"http://localhost:8080/projects_service/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == "New Project"


def test_update_project():
    project_id = test_create_project()
    payload = ProjectUpdate(name="Updated Project", description="Updated description")
    response = client.patch(f"http://localhost:8080/projects_service/projects/{project_id}", json=payload.model_dump())
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == payload.name
    assert data["description"] == payload.description


def test_delete_project():
    project_id = test_create_project()
    response = client.delete(f"http://localhost:8080/projects_service/projects/{project_id}")
    assert response.status_code == 204


def test_add_stage():
    project_id = test_create_project()
    payload = StageAdd(title="Stage 1")
    response = client.post(f"http://localhost:8080/projects_service/projects/{project_id}/stages", json=payload.model_dump())
    assert response.status_code == 200
    data = response.json()
    assert len(data["stages"]) == 1
    assert data["stages"][0]["title"] == payload.title


def test_remove_stage():
    project_id = test_create_project()
    payload = StageAdd(title="Stage 1")
    response = client.post(f"http://localhost:8080/projects_service/projects/{project_id}/stages", json=payload.model_dump())
    assert response.status_code == 200
    stage_id = response.json()["stages"][0]["id"]
    response = client.delete(f"http://localhost:8080/projects_service/projects/{project_id}/stages/{stage_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["stages"]) == 0


def test_add_attachments():
    project_id = test_create_project()
    files = [{"name": "attachment1.txt", "size": 1234, "content": "file content"}]
    payload = AttachmentsAdd(files=files)
    response = client.post(f"http://localhost:8080/projects_service/projects/{project_id}/attachments", json=payload.model_dump())
    assert response.status_code == 200
    data = response.json()
    assert len(data["attachments"]) == 1
    assert data["attachments"][0]["name"] == files[0]["name"]


def test_remove_attachment():
    project_id = test_create_project()
    files = [{"name": "attachment1.txt", "size": 1234, "content": "file content"}]
    payload = AttachmentsAdd(files=files)
    response = client.post(f"http://localhost:8080/projects_service/projects/{project_id}/attachments", json=payload.model_dump())
    assert response.status_code == 200
    attachment_name = response.json()["attachments"][0]["name"]
    response = client.delete(f"http://localhost:8080/projects_service/projects/{project_id}/attachments/{attachment_name}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["attachments"]) == 0

