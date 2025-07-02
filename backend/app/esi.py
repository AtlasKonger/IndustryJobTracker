import os
from typing import List
import requests

ESI_BASE_URL = os.getenv("ESI_BASE_URL", "https://esi.evetech.net/latest")
USER_AGENT = os.getenv("USER_AGENT", "EveIndustryTracker/1.0 (contact: corp@example.com)")


class EsiClient:
    def __init__(self, access_token: str | None = None):
        self.access_token = access_token

    def _headers(self):
        h = {"User-Agent": USER_AGENT}
        if self.access_token:
            h["Authorization"] = f"Bearer {self.access_token}"
        return h

    def get_character_industry_jobs(self, character_id: int, include_completed: bool = False) -> List[dict]:
        params = {"include_completed": str(include_completed).lower()}
        url = f"{ESI_BASE_URL}/characters/{character_id}/industry/jobs/"
        resp = requests.get(url, headers=self._headers(), params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_corporation_industry_jobs(self, corporation_id: int, include_completed: bool = False) -> List[dict]:
        params = {"include_completed": str(include_completed).lower()}
        url = f"{ESI_BASE_URL}/corporations/{corporation_id}/industry/jobs/"
        resp = requests.get(url, headers=self._headers(), params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()