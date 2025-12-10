from datetime import datetime
from typing import List

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi import APIRouter

from defects_service.model import Defect, get_db
from defects_service.schemas import DefectOut, StatsOut, DefectCreate, DefectUpdate, StatusUpdate, CommentCreate, AttachmentsAdd

app = APIRouter()


def add_history(defect: Defect, action: str, payload: dict) -> None:
    entry = {
        "ts": datetime.utcnow().isoformat(),
        "action": action,
        "payload": payload,
    }
    history = list(defect.history or [])
    history.append(entry)
    defect.history = history


@app.get("/defects", response_model=List[DefectOut])
def list_defects(db: Session = Depends(get_db)):
    items = db.query(Defect).order_by(Defect.id.desc()).all()
    return items


@app.get("/defects/stats", response_model=StatsOut)
def get_stats(db: Session = Depends(get_db)):
    total = db.query(Defect).count()
    closed = db.query(Defect).filter(Defect.status == "Закрыта").count()
    return StatsOut(total=total, closed=closed)


@app.get("/defects/{defect_id}", response_model=DefectOut)
def get_defect(defect_id: int, db: Session = Depends(get_db)):
    d = db.query(Defect).filter(Defect.id == defect_id).first()
    if not d:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Дефект не найден")
    return d


@app.post("/defects", response_model=DefectOut, status_code=status.HTTP_201_CREATED)
def create_defect(payload: DefectCreate, db: Session = Depends(get_db)):
    now = datetime.utcnow().isoformat()
    defect = Defect(
        title=payload.title.strip(),
        desc=(payload.desc or "").strip(),
        status="Новая",
        priority=payload.priority or "Средний",
        assignee=(payload.assignee or "").strip(),
        due=payload.due or "",
        attachments=[],
        comments=[],
        history=[{"ts": now, "action": "create", "payload": payload.model_dump()}],
    )
    db.add(defect)
    db.commit()
    db.refresh(defect)
    return defect


@app.patch("/defects/{defect_id}", response_model=DefectOut)
def update_defect(defect_id: int, payload: DefectUpdate, db: Session = Depends(get_db)):
    defect = db.query(Defect).filter(Defect.id == defect_id).first()
    if not defect:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Дефект не найден")

    before = {
        "title": defect.title,
        "desc": defect.desc,
        "priority": defect.priority,
        "assignee": defect.assignee,
        "due": defect.due,
        "status": defect.status,
    }

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(defect, field, value)

    add_history(defect, "update", {"before": before, "after": data})
    db.commit()
    db.refresh(defect)
    return defect


@app.patch("/defects/{defect_id}/status", response_model=DefectOut)
def update_status(defect_id: int, payload: StatusUpdate, db: Session = Depends(get_db)):
    defect = db.query(Defect).filter(Defect.id == defect_id).first()
    if not defect:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Дефект не найден")
    before = defect.status
    defect.status = payload.status
    add_history(defect, "status", {"from": before, "to": payload.status})
    db.commit()
    db.refresh(defect)
    return defect


@app.post("/defects/{defect_id}/comments", response_model=DefectOut)
def add_comment(defect_id: int, payload: CommentCreate, db: Session = Depends(get_db)):
    defect = db.query(Defect).filter(Defect.id == defect_id).first()
    if not defect:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Дефект не найден")
    comments = list(defect.comments or [])
    comment_id = int(datetime.utcnow().timestamp() * 1000)
    comment = {"id": comment_id, "text": payload.text}
    comments.append(comment)
    defect.comments = comments
    add_history(defect, "comment", {"text": payload.text})
    db.commit()
    db.refresh(defect)
    return defect


@app.post("/defects/{defect_id}/attachments", response_model=DefectOut)
def add_attachments(defect_id: int, payload: AttachmentsAdd, db: Session = Depends(get_db)):
    defect = db.query(Defect).filter(Defect.id == defect_id).first()
    if not defect:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Дефект не найден")
    attachments = list(defect.attachments or [])
    attachments.extend([f.model_dump() for f in payload.files])
    defect.attachments = attachments
    add_history(defect, "attach", {"count": len(payload.files)})
    db.commit()
    db.refresh(defect)
    return defect


@app.delete("/defects/{defect_id}/attachments/{name}", response_model=DefectOut)
def remove_attachment(defect_id: int, name: str, db: Session = Depends(get_db)):
    defect = db.query(Defect).filter(Defect.id == defect_id).first()
    if not defect:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Дефект не найден")
    attachments = [a for a in (defect.attachments or []) if a.get("name") != name]
    defect.attachments = attachments
    add_history(defect, "detach", {"name": name})
    db.commit()
    db.refresh(defect)
    return defect


@app.delete("/defects/{defect_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_defect(defect_id: int, db: Session = Depends(get_db)):
    defect = db.query(Defect).filter(Defect.id == defect_id).first()
    if not defect:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Дефект не найден")
    db.delete(defect)
    db.commit()
    return {"status": "deleted"}

