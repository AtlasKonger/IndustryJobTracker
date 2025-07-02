from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, crud
from ..deps import get_db

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/character/{character_id}", response_model=List[schemas.JobBase])
def list_character_jobs(character_id: int, db: Session = Depends(get_db)):
    jobs = crud.get_jobs_for_character(db, character_id)
    return jobs