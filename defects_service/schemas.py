from typing import List, Optional

from pydantic import BaseModel


class Attachment(BaseModel):
    name: str
    size: int
    type: Optional[str] = ""
    content: str


class Comment(BaseModel):
    id: int
    text: str


class HistoryEntry(BaseModel):
    ts: str
    action: str
    payload: dict


class DefectBase(BaseModel):
    title: str
    desc: Optional[str] = ""
    priority: str = "Средний"
    assignee: Optional[str] = ""
    due: Optional[str] = ""


class DefectCreate(DefectBase):
    pass


class DefectUpdate(BaseModel):
    title: Optional[str] = None
    desc: Optional[str] = None
    priority: Optional[str] = None
    assignee: Optional[str] = None
    due: Optional[str] = None
    status: Optional[str] = None


class DefectOut(BaseModel):
    id: int
    title: str
    desc: Optional[str]
    status: str
    priority: str
    assignee: Optional[str]
    due: Optional[str]
    attachments: List[Attachment]
    comments: List[Comment]
    history: List[HistoryEntry]

    class Config:
        from_attributes = True


class StatusUpdate(BaseModel):
    status: str


class CommentCreate(BaseModel):
    text: str


class AttachmentsAdd(BaseModel):
    files: List[Attachment]


class StatsOut(BaseModel):
    total: int
    closed: int