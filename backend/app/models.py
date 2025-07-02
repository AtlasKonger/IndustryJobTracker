from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class Corporation(Base):
    __tablename__ = "corporations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    characters = relationship("Character", back_populates="corporation")


class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    corporation_id = Column(Integer, ForeignKey("corporations.id"))

    access_token = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    token_expiry = Column(DateTime, nullable=True)

    corporation = relationship("Corporation", back_populates="characters")
    jobs = relationship("Job", back_populates="character")


class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"))
    corporation_id = Column(Integer, ForeignKey("corporations.id"))

    activity_id = Column(Integer)
    blueprint_id = Column(Integer)
    blueprint_type_id = Column(Integer)

    status = Column(String, index=True)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False)
    product_type_id = Column(Integer, nullable=True)

    raw = Column(JSON, nullable=True)

    character = relationship("Character", back_populates="jobs")


class UserRole(Base):
    """Basic role mapping for admin privileges."""

    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"))
    role = Column(String, index=True)  # e.g., 'admin'