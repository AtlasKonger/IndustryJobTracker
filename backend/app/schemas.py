from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CharacterBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class CharacterCreate(BaseModel):
    id: int
    name: str


class JobBase(BaseModel):
    job_id: int
    character_id: int
    activity_id: int
    status: str
    start_date: datetime
    end_date: Optional[datetime]
    completed: bool

    class Config:
        orm_mode = True


class JobCreate(BaseModel):
    job_id: int


class Job(JobBase):
    pass  # For now same as base, but allows extension


class Corporation(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True