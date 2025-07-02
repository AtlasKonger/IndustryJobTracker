import base64
import json
import os
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any

import requests

from .config import settings

SSO_AUTHORIZE_URL = "https://login.eveonline.com/v2/oauth/authorize"
SSO_TOKEN_URL = "https://login.eveonline.com/v2/oauth/token"
SSO_VERIFY_URL = "https://login.eveonline.com/oauth/verify"


class EveSSOError(Exception):
    pass


def _basic_auth_header(client_id: str, client_secret: str) -> str:
    b64 = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    return f"Basic {b64}"


def build_login_url(state: str) -> str:
    params = {
        "response_type": "code",
        "redirect_uri": settings.sso_redirect_uri,
        "client_id": settings.sso_client_id,
        "scope": settings.sso_scopes,
        "state": state,
    }
    import urllib.parse as up

    query = up.urlencode(params, quote_via=up.quote_plus)
    return f"{SSO_AUTHORIZE_URL}?{query}"


def exchange_code_for_tokens(code: str) -> Dict[str, Any]:
    data = {
        "grant_type": "authorization_code",
        "code": code,
    }
    headers = {
        "Authorization": _basic_auth_header(settings.sso_client_id, settings.sso_client_secret),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    resp = requests.post(SSO_TOKEN_URL, data=data, headers=headers, timeout=30)
    if resp.status_code != 200:
        raise EveSSOError(f"Token exchange failed: {resp.text}")
    return resp.json()


def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    headers = {
        "Authorization": _basic_auth_header(settings.sso_client_id, settings.sso_client_secret),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    resp = requests.post(SSO_TOKEN_URL, data=data, headers=headers, timeout=30)
    if resp.status_code != 200:
        raise EveSSOError(f"Refresh failed: {resp.text}")
    return resp.json()


def verify_access_token(access_token: str) -> Dict[str, Any]:
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(SSO_VERIFY_URL, headers=headers, timeout=30)
    if resp.status_code != 200:
        raise EveSSOError("Verify failed")
    return resp.json()


def token_expiry_datetime(expires_in: int) -> datetime:
    # Provide a 30-second grace period
    return datetime.utcnow() + timedelta(seconds=expires_in - 30)