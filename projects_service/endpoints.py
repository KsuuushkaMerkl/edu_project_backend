from datetime import datetime
from typing import List

from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session

from projects_service.model import Project, get_db
from projects_service.schemas import ProjectOut, ProjectCreate, ProjectUpdate, StageAdd, AttachmentsAdd

app = APIRouter()


def add_history(project: Project, action: str, payload: dict) -> None:
    entry = {
        "ts": datetime.utcnow().isoformat(),
        "action": action,
        "payload": payload,
    }
    history = list(project.history or [])
    history.append(entry)
    project.history = history


@app.get("/projects", response_model=List[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    items = db.query(Project).order_by(Project.id.desc()).all()
    return items


@app.get("/projects/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")
    return p


@app.post("/projects", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    now = datetime.utcnow().isoformat()
    project = Project(
        name=payload.name.strip(),
        description=(payload.description or "").strip(),
        stages=[],
        attachments=[],
        history=[{"ts": now, "action": "create", "payload": payload.model_dump()}],
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@app.patch("/projects/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")

    before = {"name": project.name, "description": project.description}
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(project, field, value)

    add_history(project, "update", {"before": before, "after": data})
    db.commit()
    db.refresh(project)
    return project


@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")
    db.delete(project)
    db.commit()
    return {"status": "deleted"}


@app.post("/projects/{project_id}/stages", response_model=ProjectOut)
def add_stage(project_id: int, payload: StageAdd, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")
    stages = list(project.stages or [])
    if any(s.get("title") == payload.title for s in stages):
        return project
    stage_id = int(datetime.utcnow().timestamp() * 1000)
    stages.append({"id": stage_id, "title": payload.title})
    project.stages = stages
    add_history(project, "stage_add", {"title": payload.title})
    db.commit()
    db.refresh(project)
    return project


@app.delete("/projects/{project_id}/stages/{stage_id}", response_model=ProjectOut)
def remove_stage(project_id: int, stage_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")
    stages = list(project.stages or [])
    removed = None
    new_stages = []
    for s in stages:
        if int(s.get("id")) == stage_id:
            removed = s
            continue
        new_stages.append(s)
    project.stages = new_stages
    add_history(project, "stage_remove", {"title": removed.get("title") if removed else stage_id})
    db.commit()
    db.refresh(project)
    return project


@app.post("/projects/{project_id}/attachments", response_model=ProjectOut)
def add_attachments(project_id: int, payload: AttachmentsAdd, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")
    attachments = list(project.attachments or [])
    attachments.extend([f.model_dump() for f in payload.files])
    project.attachments = attachments
    add_history(project, "attach", {"count": len(payload.files)})
    db.commit()
    db.refresh(project)
    return project


@app.delete("/projects/{project_id}/attachments/{name}", response_model=ProjectOut)
def remove_attachment(project_id: int, name: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")
    attachments = [a for a in (project.attachments or []) if a.get("name") != name]
    project.attachments = attachments
    add_history(project, "detach", {"name": name})
    db.commit()
    db.refresh(project)
    return project
