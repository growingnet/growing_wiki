"""Configuration models for the Growing Wiki council."""

import os

from pydantic import BaseModel, Field, SecretStr


class CouncilConfig(BaseModel):
    """Minimal configuration required to initialize the council."""

    openrouter_api_key: SecretStr
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    claim_extractor_model: str
    request_timeout_seconds: float = Field(default=60.0, gt=0)
    calibration_run_label: str = "schema-calibration"
    calibration_output_dir: str = "artifacts/calibration"

    @classmethod
    def from_env(cls, **kwargs: object) -> "CouncilConfig":
        """Build a config from explicit arguments plus `OPENROUTER_API_KEY`."""
        openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
        if not openrouter_api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is required in the environment for live runs."
            )
        return cls(openrouter_api_key=openrouter_api_key, **kwargs)
