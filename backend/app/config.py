from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    sso_client_id: str = Field(..., env="SSO_CLIENT_ID")
    sso_client_secret: str = Field(..., env="SSO_CLIENT_SECRET")
    sso_redirect_uri: str = Field("http://localhost:8000/auth/callback", env="SSO_REDIRECT_URI")
    sso_scopes: str = Field(
        "esi-industry.read_character_jobs.v1 esi-industry.read_corporation_jobs.v1",
        env="SSO_SCOPES",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()