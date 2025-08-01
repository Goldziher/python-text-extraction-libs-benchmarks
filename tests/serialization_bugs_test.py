"""Tests for serialization bugs we discovered in production."""

import json
import tempfile
from pathlib import Path

import msgspec
import pandas as pd
import pytest

from src.reporting import BenchmarkReporter
from src.types import (
    BenchmarkResult,
    BenchmarkSummary,
    DocumentCategory,
    ExtractionStatus,
    FileType,
    Framework,
)


class TestBenchmarkResultSerialization:
    """Test that BenchmarkResult serializes correctly."""

    def test_benchmark_result_has_no_success_field(self):
        """Verify BenchmarkResult doesn't have a success field."""
        result = BenchmarkResult(
            file_path="test.pdf",
            file_size=1000,
            file_type=FileType.PDF,
            category=DocumentCategory.SMALL,
            framework=Framework.KREUZBERG_SYNC,
            iteration=1,
            status=ExtractionStatus.SUCCESS,
            extraction_time=1.5,
            peak_memory_mb=100.0,
            avg_memory_mb=80.0,
            peak_cpu_percent=90.0,
            avg_cpu_percent=75.0,
            character_count=100,
            word_count=20,
        )

        # This should not exist
        with pytest.raises(AttributeError):
            _ = result.success

    def test_benchmark_result_status_field_exists(self):
        """Verify BenchmarkResult has status field."""
        result = BenchmarkResult(
            file_path="test.pdf",
            file_size=1000,
            file_type=FileType.PDF,
            category=DocumentCategory.SMALL,
            framework=Framework.KREUZBERG_SYNC,
            iteration=1,
            status=ExtractionStatus.SUCCESS,
            extraction_time=1.5,
            peak_memory_mb=100.0,
            avg_memory_mb=80.0,
            peak_cpu_percent=90.0,
            avg_cpu_percent=75.0,
        )

        assert result.status == ExtractionStatus.SUCCESS
        assert isinstance(result.status, ExtractionStatus)

    def test_msgspec_serialization_of_benchmark_result(self):
        """Test that msgspec correctly serializes BenchmarkResult."""
        result = BenchmarkResult(
            file_path="test.pdf",
            file_size=1000,
            file_type=FileType.PDF,
            category=DocumentCategory.SMALL,
            framework=Framework.KREUZBERG_SYNC,
            iteration=1,
            status=ExtractionStatus.SUCCESS,
            extraction_time=1.5,
            peak_memory_mb=100.0,
            avg_memory_mb=80.0,
            peak_cpu_percent=90.0,
            avg_cpu_percent=75.0,
            character_count=100,
            word_count=20,
        )

        # Serialize with msgspec
        serialized = msgspec.json.encode(result)
        data = json.loads(serialized)

        # Verify structure
        assert "status" in data
        assert data["status"] == "success"
        assert "success" not in data  # This field should not exist

    def test_msgspec_deserialization_of_benchmark_result(self):
        """Test that msgspec correctly deserializes BenchmarkResult."""
        data = {
            "file_path": "test.pdf",
            "file_size": 1000,
            "file_type": "pdf",
            "category": "small",
            "framework": "kreuzberg_sync",
            "iteration": 1,
            "status": "success",
            "extraction_time": 1.5,
            "peak_memory_mb": 100.0,
            "avg_memory_mb": 80.0,
            "peak_cpu_percent": 90.0,
            "avg_cpu_percent": 75.0,
            "character_count": 100,
            "word_count": 20,
        }

        # Deserialize with msgspec
        result = msgspec.json.decode(json.dumps(data).encode(), type=BenchmarkResult)

        assert result.status == ExtractionStatus.SUCCESS
        assert result.extraction_time == 1.5


class TestReportingBugs:
    """Test the reporting module bugs we discovered."""

    def test_csv_export_with_status_field(self):
        """Test CSV export correctly uses status field, not success."""
        results = [
            BenchmarkResult(
                file_path="test1.pdf",
                file_size=1000,
                file_type=FileType.PDF,
                category=DocumentCategory.SMALL,
                framework=Framework.KREUZBERG_SYNC,
                iteration=1,
                status=ExtractionStatus.SUCCESS,
                extraction_time=1.5,
                peak_memory_mb=100.0,
                avg_memory_mb=90.0,
                peak_cpu_percent=60.0,
                avg_cpu_percent=50.0,
                character_count=100,
            ),
            BenchmarkResult(
                file_path="test2.pdf",
                file_size=2000,
                file_type=FileType.PDF,
                category=DocumentCategory.SMALL,
                framework=Framework.KREUZBERG_SYNC,
                iteration=1,
                status=ExtractionStatus.FAILED,
                extraction_time=0.5,
                peak_memory_mb=50.0,
                avg_memory_mb=45.0,
                peak_cpu_percent=30.0,
                avg_cpu_percent=25.0,
                error_message="Test error",
            ),
        ]

        summaries = [
            BenchmarkSummary(
                framework=Framework.KREUZBERG_SYNC,
                category=DocumentCategory.SMALL,
                total_files=2,
                successful_files=1,
                failed_files=1,
                partial_files=0,
                timeout_files=0,
                avg_extraction_time=1.0,
                median_extraction_time=1.0,
                min_extraction_time=0.5,
                max_extraction_time=1.5,
                avg_peak_memory_mb=75.0,
                avg_cpu_percent=37.5,
                success_rate=0.5,
                files_per_second=1.0,
                mb_per_second=1.5,
            ),
        ]

        reporter = BenchmarkReporter(results, summaries)

        # Export to CSV
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            output_path = Path(f.name)

        try:
            reporter.save_results_csv(output_path)

            # Read back and verify
            df = pd.read_csv(output_path)

            # Check that success column exists and has correct values
            assert "success" in df.columns
            assert df.iloc[0]["success"]  # First result is SUCCESS
            assert not df.iloc[1]["success"]  # Second result is FAILED

        finally:
            output_path.unlink()

    def test_csv_export_with_none_fields(self):
        """Test CSV export handles None fields correctly."""
        result = BenchmarkResult(
            file_path="test.pdf",
            file_size=1000,
            file_type=FileType.PDF,
            category=DocumentCategory.SMALL,
            framework=Framework.KREUZBERG_SYNC,
            iteration=1,
            status=ExtractionStatus.FAILED,
            extraction_time=0.0,  # Required field, can't be None
            peak_memory_mb=0.0,  # Required field
            avg_memory_mb=0.0,  # Required field
            peak_cpu_percent=0.0,  # Required field
            avg_cpu_percent=0.0,  # Required field
            error_message="Missing dependency",
        )

        summaries = []
        reporter = BenchmarkReporter([result], summaries)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            output_path = Path(f.name)

        try:
            reporter.save_results_csv(output_path)
            df = pd.read_csv(output_path)

            # Fields will be 0.0 since we can't have None in required fields
            assert df.iloc[0]["extraction_time_seconds"] == 0.0
            assert df.iloc[0]["memory_peak_mb"] == 0.0
            assert df.iloc[0]["cpu_percent"] == 0.0

        finally:
            output_path.unlink()


class TestAggregationWithFailedResults:
    """Test aggregation logic with failed/incomplete results."""

    def test_aggregation_with_all_failed_results(self):
        """Test aggregation when all results have failed status."""
        import tempfile

        from src.aggregate import ResultAggregator

        aggregator = ResultAggregator()

        # Create results where all extractions failed
        results = [
            BenchmarkResult(
                file_path=f"test{i}.pdf",
                file_size=1000,
                file_type=FileType.PDF,
                category=DocumentCategory.LARGE,
                framework=Framework.KREUZBERG_ASYNC,
                iteration=1,
                status=ExtractionStatus.FAILED,
                extraction_time=0.1,  # Required field
                peak_memory_mb=10.0,
                avg_memory_mb=10.0,
                peak_cpu_percent=5.0,
                avg_cpu_percent=5.0,
                error_type="MissingDependencyError",
                error_message="The 'deep-translator' library is not installed",
            )
            for i in range(3)
        ]

        # Save results to temp dir and aggregate
        with tempfile.TemporaryDirectory() as tmpdir:
            results_path = Path(tmpdir) / "benchmark_results.json"
            with open(results_path, "wb") as f:
                f.write(msgspec.json.encode(results))

            aggregated = aggregator.aggregate_results([Path(tmpdir)])

            # Find the kreuzberg_async large summary
            summaries = aggregated.framework_summaries.get(Framework.KREUZBERG_ASYNC, [])
            summary = next(s for s in summaries if s.category == DocumentCategory.LARGE)

        assert summary.successful_files == 0
        assert summary.failed_files == 3
        assert summary.success_rate == 0.0
        assert summary.files_per_second is None or summary.files_per_second == 0

    def test_aggregation_with_mixed_results(self):
        """Test aggregation with mix of success and failed results."""
        import tempfile

        from src.aggregate import ResultAggregator

        aggregator = ResultAggregator()

        results = [
            BenchmarkResult(
                file_path="success.pdf",
                file_size=1000,
                file_type=FileType.PDF,
                category=DocumentCategory.SMALL,
                framework=Framework.UNSTRUCTURED,
                iteration=1,
                status=ExtractionStatus.SUCCESS,
                extraction_time=2.0,
                peak_memory_mb=100.0,
                avg_memory_mb=80.0,
                peak_cpu_percent=70.0,
                avg_cpu_percent=60.0,
                character_count=1000,
                word_count=200,
            ),
            BenchmarkResult(
                file_path="failed.pdf",
                file_size=2000,
                file_type=FileType.PDF,
                category=DocumentCategory.SMALL,
                framework=Framework.UNSTRUCTURED,
                iteration=1,
                status=ExtractionStatus.FAILED,
                extraction_time=0.0,
                peak_memory_mb=50.0,
                avg_memory_mb=40.0,
                peak_cpu_percent=20.0,
                avg_cpu_percent=15.0,
                error_message="Timeout",
            ),
            BenchmarkResult(
                file_path="timeout.pdf",
                file_size=3000,
                file_type=FileType.PDF,
                category=DocumentCategory.SMALL,
                framework=Framework.UNSTRUCTURED,
                iteration=1,
                status=ExtractionStatus.TIMEOUT,
                extraction_time=300.0,  # Timed out at limit
                peak_memory_mb=200.0,
                avg_memory_mb=150.0,
                peak_cpu_percent=90.0,
                avg_cpu_percent=85.0,
            ),
        ]

        # Save results to temp dir and aggregate
        with tempfile.TemporaryDirectory() as tmpdir:
            results_path = Path(tmpdir) / "benchmark_results.json"
            with open(results_path, "wb") as f:
                f.write(msgspec.json.encode(results))

            aggregated = aggregator.aggregate_results([Path(tmpdir)])

            # Get unstructured summary
            summaries = aggregated.framework_summaries.get(Framework.UNSTRUCTURED, [])
            summary = summaries[0]

        assert summary.successful_files == 1
        assert summary.failed_files == 1
        assert summary.timeout_files == 1
        assert summary.success_rate == pytest.approx(1 / 3)


class TestGenerateIndexNoneHandling:
    """Test generate_index.py None value handling."""

    def test_generate_performance_table_with_none_speeds(self):
        """Test performance table generation with None speed values."""
        from src.generate_index import generate_performance_table

        # Mock framework stats with None values
        framework_stats = {
            "kreuzberg_async": {
                "category_speeds": {
                    "tiny": 10.5,
                    "small": 5.2,
                    "medium": None,  # None value
                    "large": None,  # None value
                    "huge": 0.0,  # Zero value
                },
                "success_rate": 60.0,
                "failure_breakdown": ["3 timeouts", "2 errors"],
                "avg_memory": 500.0,
                "install_size": "71MB",
            }
        }

        sorted_frameworks = sorted(framework_stats.items(), key=lambda x: x[1]["success_rate"], reverse=True)

        # Add install sizes dict required by the function
        install_sizes = {"kreuzberg_async": "71MB"}

        # This should not raise TypeError
        html = generate_performance_table(sorted_frameworks, install_sizes)

        assert "<td>10.50</td>" in html  # tiny speed
        assert "<td>5.20</td>" in html  # small speed
        assert "<td>-</td>" in html  # None values should show as dash
        assert html.count("<td>-</td>") >= 2  # At least 2 None values

    def test_generate_memory_table_with_none_values(self):
        """Test memory table generation with None memory values."""
        from src.generate_index import generate_memory_table

        framework_stats = {
            "docling": {
                "category_memories": {
                    "tiny": 1500.0,
                    "small": None,  # None value
                    "medium": 0.0,  # Zero value
                    "large": None,  # None value
                    "huge": None,  # None value
                },
                "avg_memory": None,  # None average
            }
        }

        sorted_frameworks = list(framework_stats.items())

        # This should not raise TypeError
        html = generate_memory_table(sorted_frameworks)

        assert "<td>1500</td>" in html  # tiny memory
        assert "<td>-</td>" in html  # None values
        assert "<td>N/A</td>" in html  # None avg_memory


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
