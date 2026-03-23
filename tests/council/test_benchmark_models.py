from pathlib import Path

from growing_wiki_council.models.benchmark import BenchmarkDataset


def test_benchmark_dataset_loads_supported_source_types(tmp_path: Path) -> None:
    """The benchmark manifest loader accepts the supported source kinds."""
    manifest_path = tmp_path / "benchmark.json"
    manifest_path.write_text(
        """
        {
          "dataset_name": "real-paper-benchmark",
          "entries": [
            {
              "paper_id": "paper-a",
              "source_type": "pdf_path",
              "source": "fixtures/a.pdf"
            },
            {
              "paper_id": "paper-b",
              "source_type": "arxiv_id",
              "source": "1511.05641"
            }
          ]
        }
        """.strip(),
        encoding="utf-8",
    )

    dataset = BenchmarkDataset.load(manifest_path)

    assert dataset.dataset_name == "real-paper-benchmark"
    assert dataset.entries[0].source_type == "pdf_path"
    assert dataset.entries[1].source_type == "arxiv_id"
