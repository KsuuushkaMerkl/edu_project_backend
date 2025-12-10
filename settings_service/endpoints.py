from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session

from settings_service.model import StageOption, get_db
from settings_service.schemas import StageOptionsList, StageOptionOut, StageOptionCreate

app = APIRouter()

DEFAULTS = ["Анализ", "В разработке", "Выполнено"]


def ensure_defaults(db: Session) -> None:
    count = db.query(StageOption).count()
    if count == 0:
        for name in DEFAULTS:
            db.add(StageOption(name=name))
        db.commit()


def ensure_defaults(db: Session) -> None:
    count = db.query(StageOption).count()
    if count == 0:
        for name in DEFAULTS:
            db.add(StageOption(name=name))
        db.commit()


@app.get("/settings/stages", response_model=StageOptionsList)
def list_stage_options(db: Session = Depends(get_db)):
    ensure_defaults(db)
    items = db.query(StageOption).order_by(StageOption.id).all()
    return StageOptionsList(items=items)


@app.post("/settings/stages", response_model=StageOptionOut, status_code=status.HTTP_201_CREATED)
def add_stage_option(payload: StageOptionCreate, db: Session = Depends(get_db)):
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Имя этапа не может быть пустым")
    existing = db.query(StageOption).filter(StageOption.name == name).first()
    if existing:
        return existing
    item = StageOption(name=name)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.delete("/settings/stages/{name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stage_option(name: str, db: Session = Depends(get_db)):
    item = db.query(StageOption).filter(StageOption.name == name).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Этап не найден")
    db.delete(item)
    db.commit()
    return {"status": "deleted"}


@app.post("/settings/stages/reset", response_model=StageOptionsList)
def reset_stage_options(db: Session = Depends(get_db)):
    db.query(StageOption).delete()
    db.commit()
    for name in DEFAULTS:
        db.add(StageOption(name=name))
    db.commit()
    items = db.query(StageOption).order_by(StageOption.id).all()
    return StageOptionsList(items=items)
