from sqlalchemy.orm import Session
from . import models
from . import schemas
from typing import List


def get_character(db: Session, character_id: int) -> models.Character | None:
    return db.query(models.Character).filter(models.Character.id == character_id).first()


def create_character(db: Session, character: schemas.CharacterCreate) -> models.Character:
    db_character = models.Character(id=character.id, name=character.name)
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character


def get_jobs_for_character(db: Session, character_id: int) -> List[models.Job]:
    return db.query(models.Job).filter(models.Job.character_id == character_id).all()


def upsert_job(db: Session, job_data: dict, character_id: int, corporation_id: int | None = None):
    job_id = job_data.get("job_id")
    db_job = db.query(models.Job).filter(models.Job.job_id == job_id).first()
    if db_job is None:
        db_job = models.Job(job_id=job_id, character_id=character_id, corporation_id=corporation_id)
    # Update fields
    db_job.activity_id = job_data.get("activity_id")
    db_job.blueprint_id = job_data.get("blueprint_id")
    db_job.blueprint_type_id = job_data.get("blueprint_type_id")
    db_job.status = job_data.get("status")
    db_job.start_date = job_data.get("start_date")
    db_job.end_date = job_data.get("end_date")
    db_job.completed = job_data.get("completed", False)
    db_job.product_type_id = job_data.get("product_type_id")
    db_job.raw = job_data

    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job