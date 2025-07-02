import secrets
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime

from ..auth import build_login_url, exchange_code_for_tokens, verify_access_token, token_expiry_datetime, EveSSOError
from ..deps import get_db
from .. import crud, models, schemas

router = APIRouter(prefix="/auth", tags=["auth"])

STATE_COOKIE_NAME = "eve_state"
STATE_TTL = 600  # seconds


@router.get("/login")
def login(request: Request):
    state = secrets.token_urlsafe(16)
    url = build_login_url(state)
    response = RedirectResponse(url)
    # store state in cookie for CSRF protection
    response.set_cookie(STATE_COOKIE_NAME, state, max_age=STATE_TTL, httponly=True, secure=False)
    return response


@router.get("/callback")
def callback(request: Request, code: str | None = None, state: str | None = None, db: Session = Depends(get_db)):
    stored_state = request.cookies.get(STATE_COOKIE_NAME)
    if stored_state is None or state != stored_state:
        raise HTTPException(status_code=400, detail="Invalid state")

    if code is None:
        raise HTTPException(status_code=400, detail="Missing code")

    try:
        token_data = exchange_code_for_tokens(code)
    except EveSSOError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]
    expires_in = token_data["expires_in"]

    # Verify token to get character id & name
    verify_data = verify_access_token(access_token)
    char_id = int(verify_data["CharacterID"])
    char_name = verify_data["CharacterName"]

    # Fetch or create character
    character = crud.get_character(db, char_id)
    if character is None:
        character = crud.create_character(db, schemas.CharacterCreate(id=char_id, name=char_name))

    crud.update_character_tokens(db, character, access_token, refresh_token, expires_in)

    # Simple response with token (in production, set cookie or redirect to frontend)
    return JSONResponse({"message": "Authentication successful", "access_token": access_token})