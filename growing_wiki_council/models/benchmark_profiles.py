"""Benchmark profile models for steerability experiments."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

BenchmarkProfileId = Literal[
    "baseline",
    "baseline_prompt_variant",
    "website_aligned",
]


class BenchmarkProfileConfig(BaseModel):
    """Configuration for one benchmark profile."""

    profile_id: BenchmarkProfileId
    schema_variant: str | None = None

    def model_post_init(self, __context: object) -> None:
        """Default the schema variant to the selected profile."""
        if self.schema_variant is None:
            self.schema_variant = self.profile_id
