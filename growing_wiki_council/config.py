"""Configuration models for the Growing Wiki council."""

from pydantic import BaseModel, Field, SecretStr


class CouncilConfig(BaseModel):
    """Minimal configuration required to initialize the council."""

    openrouter_api_key: SecretStr
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    claim_extractor_model: str
    request_timeout_seconds: float = Field(default=60.0, gt=0)
    calibration_run_label: str = "schema-calibration"
    calibration_output_dir: str = "artifacts/calibration"
