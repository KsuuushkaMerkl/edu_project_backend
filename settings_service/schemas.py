from typing import List

from pydantic import BaseModel


class StageOptionOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class StageOptionCreate(BaseModel):
    name: str


class StageOptionsList(BaseModel):
    items: List[StageOptionOut]