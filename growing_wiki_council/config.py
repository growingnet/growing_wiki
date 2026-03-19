"""Configuration models for the Growing Wiki council."""

from pydantic import BaseModel


class CouncilConfig(BaseModel):
    """Minimal configuration required to initialize the council."""

    openrouter_api_key: str
