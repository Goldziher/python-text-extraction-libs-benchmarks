"""Document and test field mapping issues between types and reporting."""

import pytest

from src.types import BenchmarkResult, BenchmarkSummary, DocumentCategory, ExtractionStatus, FileType, Framework


class TestFieldMapping:
    """Document the field mapping issues we found."""

    def test_benchmark_result_field_mapping(self):
        """Document actual vs expected field names in BenchmarkResult."""
        # Fields that reporting.py expects but don't exist
        expected_but_missing = {
            "file_size_bytes": "file_size",  # actual field name
            "extraction_time_seconds": "extraction_time",
            "memory_peak_mb": "peak_memory_mb",  # close but not exact
            "cpu_percent": "avg_cpu_percent",  # or peak_cpu_percent?
            "success": "status (computed as status == ExtractionStatus.SUCCESS)",
            "extracted_text_length": "character_count",
        }

        # Create a result to verify actual fields
        result = BenchmarkResult(
            file_path="test.pdf",
            file_size=1000,
            file_type=FileType.PDF,
            category=DocumentCategory.SMALL,
            framework=Framework.KREUZBERG_SYNC,
            iteration=1,
            extraction_time=1.5,
            peak_memory_mb=100.0,
            avg_memory_mb=80.0,
            peak_cpu_percent=90.0,
            avg_cpu_percent=75.0,
            status=ExtractionStatus.SUCCESS,
        )

        # Verify mapping
        assert result.file_size == 1000  # not file_size_bytes
        assert result.extraction_time == 1.5  # not extraction_time_seconds
        assert result.peak_memory_mb == 100.0  # correct
        assert result.avg_cpu_percent == 75.0  # not cpu_percent
        assert result.status == ExtractionStatus.SUCCESS  # not success
        assert result.character_count is None  # not extracted_text_length

    def test_benchmark_summary_field_mapping(self):
        """Document actual vs expected field names in BenchmarkSummary."""
        # Fields that reporting.py expects but don't exist
        expected_but_missing = {
            "successful_extractions": "successful_files",
            "failed_extractions": "failed_files",
            "average_time_seconds": "avg_extraction_time",
            "median_time_seconds": "median_extraction_time",
            "min_time_seconds": "min_extraction_time",
            "max_time_seconds": "max_extraction_time",
            "average_memory_mb": "avg_peak_memory_mb",
            "average_cpu_percent": "avg_cpu_percent",  # this one is correct!
            "total_time_seconds": "doesn't exist - need to calculate",
            "file_type": "doesn't exist - summaries are per framework/category",
        }

        # Create a summary to verify actual fields
        summary = BenchmarkSummary(
            framework=Framework.KREUZBERG_SYNC,
            category=DocumentCategory.SMALL,
            total_files=10,
            successful_files=8,
            failed_files=2,
            partial_files=0,
            timeout_files=0,
            avg_extraction_time=2.5,
            median_extraction_time=2.0,
            min_extraction_time=1.0,
            max_extraction_time=5.0,
            avg_peak_memory_mb=100.0,
            avg_cpu_percent=75.0,
            success_rate=0.8,
            files_per_second=4.0,
            mb_per_second=10.0,
        )

        # Verify mapping
        assert summary.successful_files == 8  # not successful_extractions
        assert summary.failed_files == 2  # not failed_extractions
        assert summary.avg_extraction_time == 2.5  # not average_time_seconds
        assert summary.median_extraction_time == 2.0  # not median_time_seconds
        assert summary.avg_peak_memory_mb == 100.0  # not average_memory_mb
        assert summary.avg_cpu_percent == 75.0  # this one is correct!
        assert not hasattr(summary, "file_type")  # doesn't exist
        assert not hasattr(summary, "total_time_seconds")  # doesn't exist

    def test_reporting_assumptions(self):
        """Test what the reporting module assumes vs reality."""
        # The reporting module seems to expect a different data model
        # It expects summaries to have:
        # - file_type (but summaries are per framework/category, not file type)
        # - successful_extractions instead of successful_files
        # - average_time_seconds instead of avg_extraction_time
        # - etc.

        # This suggests the reporting module was written for a different
        # version of the data model or was never tested with actual data

        # Document the required transformations
        summary_transformations = {
            "successful_extractions": lambda s: s.successful_files,
            "failed_extractions": lambda s: s.failed_files,
            "average_time_seconds": lambda s: s.avg_extraction_time,
            "median_time_seconds": lambda s: s.median_extraction_time,
            "min_time_seconds": lambda s: s.min_extraction_time,
            "max_time_seconds": lambda s: s.max_extraction_time,
            "average_memory_mb": lambda s: s.avg_peak_memory_mb,
            "average_cpu_percent": lambda s: s.avg_cpu_percent,
            "total_time_seconds": lambda s: s.avg_extraction_time * s.successful_files if s.avg_extraction_time else 0,
        }

        result_transformations = {
            "file_size_bytes": lambda r: r.file_size,
            "extraction_time_seconds": lambda r: r.extraction_time,
            "memory_peak_mb": lambda r: r.peak_memory_mb,
            "cpu_percent": lambda r: r.avg_cpu_percent,
            "success": lambda r: r.status == ExtractionStatus.SUCCESS,
            "extracted_text_length": lambda r: r.character_count,
        }

        # These transformations would need to be applied in reporting.py
        assert len(summary_transformations) == 9
        assert len(result_transformations) == 6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
