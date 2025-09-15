import json

import msgspec
import pytest

from src.types import (
    BenchmarkResult,
    BenchmarkSummary,
    DocumentCategory,
    ExtractionStatus,
    FileType,
    Framework,
)


def create_test_result(status: ExtractionStatus = ExtractionStatus.SUCCESS, **kwargs) -> BenchmarkResult:
    defaults = {
        "file_path": "test.pdf",
        "file_size": 1000,
        "file_type": FileType.PDF,
        "category": DocumentCategory.SMALL,
        "framework": Framework.KREUZBERG_SYNC,
        "iteration": 1,
        "extraction_time": 1.5,
        "peak_memory_mb": 100.0,
        "avg_memory_mb": 80.0,
        "peak_cpu_percent": 90.0,
        "avg_cpu_percent": 75.0,
        "status": status,
    }
    defaults.update(kwargs)
    return BenchmarkResult(**defaults)


class TestCriticalBugs:
    def test_benchmark_result_fields_used_by_reporting(self):
        result = create_test_result()

        assert not hasattr(result, "success")
        assert not hasattr(result, "file_size_bytes")
        assert not hasattr(result, "extraction_time_seconds")
        assert not hasattr(result, "memory_peak_mb")
        assert not hasattr(result, "cpu_percent")
        assert not hasattr(result, "extracted_text_length")

        assert hasattr(result, "status")
        assert hasattr(result, "file_size")
        assert hasattr(result, "extraction_time")
        assert hasattr(result, "peak_memory_mb")
        assert hasattr(result, "avg_cpu_percent")
        assert hasattr(result, "character_count")

    def test_reporting_csv_export_field_mapping(self):
        result = create_test_result(character_count=1000, error_message="Test error")

        field_mapping = {
            "file_size_bytes": result.file_size,
            "extraction_time_seconds": result.extraction_time,
            "memory_peak_mb": result.peak_memory_mb,
            "cpu_percent": result.avg_cpu_percent,
            "success": result.status == ExtractionStatus.SUCCESS,
            "error_message": result.error_message,
            "extracted_text_length": result.character_count,
        }

        for report_field, value in field_mapping.items():
            assert value is not None or report_field == "error_message"

    def test_aggregation_with_missing_dependency_error(self):
        results = [
            BenchmarkResult(
                file_path=f"test{i}.pdf",
                file_size=1000 * (i + 1),
                file_type=FileType.PDF,
                category=DocumentCategory.LARGE,
                framework=Framework.KREUZBERG_ASYNC,
                iteration=1,
                extraction_time=0.001,
                peak_memory_mb=50.0,
                avg_memory_mb=40.0,
                peak_cpu_percent=10.0,
                avg_cpu_percent=5.0,
                status=ExtractionStatus.FAILED,
                error_type="MissingDependencyError",
                error_message="MissingDependencyError: The 'deep-translator' library is not installed. Please install it with: pip install 'kreuzberg[auto-classify-document-type]'",
            )
            for i in range(3)
        ]

        for result in results:
            serialized = msgspec.json.encode(result)
            data = json.loads(serialized)

            assert data["status"] == "failed"
            assert "MissingDependencyError" in data["error_message"]
            assert data["error_type"] == "MissingDependencyError"

    def test_generate_index_none_handling(self):
        framework_stats = {
            "kreuzberg_async": {
                "category_speeds": {
                    "tiny": None,
                    "small": None,
                    "medium": None,
                    "large": None,
                    "huge": None,
                },
                "category_memories": {
                    "tiny": None,
                    "small": None,
                    "medium": None,
                    "large": None,
                    "huge": None,
                },
                "success_rate": 0.0,
                "successful_files": 0,
                "failure_breakdown": ["276 errors"],
                "avg_memory": None,
                "install_size": "71MB",
            }
        }

        speeds = framework_stats["kreuzberg_async"]["category_speeds"]
        memories = framework_stats["kreuzberg_async"]["category_memories"]

        for cat in ["tiny", "small", "medium", "large", "huge"]:
            speed = speeds[cat]
            memory = memories[cat]

            speed_display = f"{speed:.2f}" if speed is not None and speed > 0 else "-"

            memory_display = f"{memory:.0f}" if memory is not None and memory > 0 else "-"

            assert speed_display == "-"
            assert memory_display == "-"

        avg_memory = framework_stats["kreuzberg_async"]["avg_memory"]
        avg_memory_display = f"{avg_memory:.0f}" if avg_memory and avg_memory > 0 else "N/A"
        assert avg_memory_display == "N/A"

    def test_summary_calculation_with_all_failed(self):
        summary = BenchmarkSummary(
            framework=Framework.KREUZBERG_ASYNC,
            category=DocumentCategory.LARGE,
            total_files=9,
            successful_files=0,
            failed_files=9,
            partial_files=0,
            timeout_files=0,
            avg_extraction_time=None,
            median_extraction_time=None,
            min_extraction_time=None,
            max_extraction_time=None,
            avg_peak_memory_mb=None,
            avg_cpu_percent=None,
            success_rate=0.0,
            files_per_second=None,
            mb_per_second=None,
        )

        assert summary.successful_files == 0
        assert summary.failed_files == 9
        assert summary.success_rate == 0.0
        assert summary.files_per_second is None


class TestRegressionPrevention:
    def test_reporting_module_field_access(self):
        result = create_test_result()

        required_mapping = {
            "file_size_bytes": "file_size",
            "extraction_time_seconds": "extraction_time",
            "memory_peak_mb": "peak_memory_mb",
            "cpu_percent": "avg_cpu_percent",
            "success": "status == ExtractionStatus.SUCCESS",
            "extracted_text_length": "character_count",
        }

        for actual in required_mapping.values():
            if " == " not in actual:
                assert hasattr(result, actual), f"BenchmarkResult missing {actual} field"

    def test_none_value_serialization(self):
        result = create_test_result(
            extraction_time=None,
            character_count=None,
            word_count=None,
            error_message="Dependency missing",
        )

        serialized = msgspec.json.encode(result)
        data = json.loads(serialized)

        assert data["extraction_time"] is None
        assert data["character_count"] is None
        assert data["word_count"] is None
        assert data["error_message"] == "Dependency missing"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
