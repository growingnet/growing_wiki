"""Structured models for real-paper benchmark artifacts."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BenchmarkPaperRun(BaseModel):
    """Capture one paper-level benchmark run and its serialized artifacts."""

    paper_id: str
    run_label: str
    model_id: str
    status: str
    benchmark_entry: dict[str, Any]
    provider_result: dict[str, Any] = Field(default_factory=dict)
    evidence_bundle: dict[str, Any] = Field(default_factory=dict)
    raw_review_output: dict[str, Any] = Field(default_factory=dict)
    validated_reviewer_report: dict[str, Any] = Field(default_factory=dict)
    summary_markdown: str
    error_type: str | None = None
    error_message: str | None = None


class BenchmarkRunSummary(BaseModel):
    """Capture the aggregate state of a benchmark run for one model."""

    run_label: str
    model_id: str
    dataset_name: str
    paper_runs: list[BenchmarkPaperRun] = Field(default_factory=list)
    manifest_snapshot: dict[str, Any] = Field(default_factory=dict)
    completed_paper_count: int = 0
    failed_paper_count: int = 0
