"""Configuration via Pydantic Settings."""
from pydantic_settings import BaseSettings
from pydantic import Field
class Settings(BaseSettings):
    model: str = Field(default="openrouter/owl-alpha")
    provider: str = Field(default="openrouter")
    base_url: str = Field(default="https://openrouter.ai/api/v1")
    api_key: str = Field(default="")
    openrouter_api_key: str = Field(default="")
    tools_timeout: int = Field(default=300)
    max_cost: float = Field(default=50.0)
    output_dir: str = Field(default="results")
    scope_strict: bool = Field(default=True)
    log_level: str = Field(default="info")
_settings = None
def get_settings():
    global _settings
    if _settings is None: _settings = Settings()
    return _settings
