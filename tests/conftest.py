import tempfile
from collections.abc import Generator
from pathlib import Path

import msgspec
import pytest

from src.types import AggregatedResults, BenchmarkResult, BenchmarkSummary


@pytest.fixture
def temp_dir() -> Generator[Path]:
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def aggregated_results_file(fixtures_dir: Path) -> Path:
    return fixtures_dir / "aggregated-benchmark-results-17369154065" / "aggregated_results.json"


@pytest.fixture
def aggregated_results(aggregated_results_file: Path) -> AggregatedResults:
    with open(aggregated_results_file, "rb") as f:
        return msgspec.json.decode(f.read(), type=AggregatedResults)


@pytest.fixture
def sample_benchmark_result() -> BenchmarkResult:
    from src.types import BenchmarkMetadata, BenchmarkMetrics

    return BenchmarkResult(
        metadata=BenchmarkMetadata(
            file_path="test.pdf",
            framework="test_framework",
            file_size_bytes=1024,
            category="small",
            status="success",
            error_message=None,
        ),
        metrics=BenchmarkMetrics(extraction_time=0.5, peak_memory_mb=100.0, avg_cpu_percent=25.0),
    )


@pytest.fixture
def sample_benchmark_summary() -> BenchmarkSummary:
    return BenchmarkSummary(
        framework="test_framework",
        category="small",
        total_files=10,
        successful_files=9,
        failed_files=1,
        timeout_files=0,
        avg_extraction_time=0.5,
        median_extraction_time=0.4,
        avg_peak_memory_mb=100.0,
        avg_cpu_percent=25.0,
        total_size_mb=10.0,
        files_per_second=2.0,
        mb_per_second=20.0,
    )


@pytest.fixture
def charts_dir(temp_dir: Path) -> Path:
    charts = temp_dir / "charts"
    charts.mkdir()

    (charts / "performance_comparison_large.png").write_text("fake png content")
    (charts / "interactive_dashboard.html").write_text("<html>fake dashboard</html>")

    return charts


@pytest.fixture
def docs_dir(temp_dir: Path) -> Path:
    docs = temp_dir / "docs"
    docs.mkdir()
    return docs


@pytest.fixture
def mock_cli_args():
    class MockArgs:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    return MockArgs
