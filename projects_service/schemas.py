from typing import List, Optional
from pydantic import BaseModel


class Stage(BaseModel):
    id: int
    title: str


class Attachment(BaseModel):
    name: str
    size: int
    type: Optional[str] = ""
    content: str


class HistoryEntry(BaseModel):
    ts: str
    action: str
    payload: dict


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = ""


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    stages: List[Stage]
    attachments: List[Attachment]
    history: List[HistoryEntry]

    class Config:
        from_attributes = True


class StageAdd(BaseModel):
    title: str


class AttachmentsAdd(BaseModel):
    files: List[Attachment]
