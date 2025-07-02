from datetime import datetime, timedelta
from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from . import crud, models
from .deps import get_db
from .auth import EveSSOError, refresh_access_token

http_bearer = HTTPBearer(auto_error=False)


def get_current_character(
    credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer),
    db: Session = Depends(get_db),
) -> models.Character:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = credentials.credentials

    # Find character by access token
    character = db.query(models.Character).filter(models.Character.access_token == token).first()
    if character is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # If token expired or about to expire, refresh
    if character.token_expiry and character.token_expiry < datetime.utcnow() + timedelta(seconds=30):
        try:
            data = refresh_access_token(character.refresh_token)
        except EveSSOError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token refresh failed")
        crud.update_character_tokens(
            db,
            character,
            data["access_token"],
            data.get("refresh_token", character.refresh_token),
            data["expires_in"],
        )
    return character