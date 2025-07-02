from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas, models
from ..deps import get_db
from ..esi import EsiClient

router = APIRouter(prefix="/characters", tags=["characters"])


@router.post("/", response_model=schemas.CharacterBase)
def register_character(character: schemas.CharacterCreate, db: Session = Depends(get_db)):
    db_char = crud.get_character(db, character.id)
    if db_char:
        raise HTTPException(status_code=400, detail="Character already registered")
    return crud.create_character(db, character)


@router.get("/{character_id}", response_model=schemas.CharacterBase)
def get_character(character_id: int, db: Session = Depends(get_db)):
    db_char = crud.get_character(db, character_id)
    if not db_char:
        raise HTTPException(status_code=404, detail="Character not found")
    return db_char


@router.post("/{character_id}/sync_jobs", response_model=List[schemas.JobBase])
def sync_character_jobs(character_id: int, include_completed: bool = False, db: Session = Depends(get_db)):
    db_char = crud.get_character(db, character_id)
    if not db_char:
        raise HTTPException(status_code=404, detail="Character not found")

    esi_client = EsiClient(access_token=db_char.access_token)
    try:
        jobs = esi_client.get_character_industry_jobs(character_id, include_completed=include_completed)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"ESI error: {exc}")

    out = []
    for job in jobs:
        db_job = crud.upsert_job(db, job, character_id, db_char.corporation_id)
        out.append(db_job)
    return out