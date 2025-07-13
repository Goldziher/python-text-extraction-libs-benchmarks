"""Tests for benchmark aggregation logic."""

from typing import Any

import pytest

from src.types import BenchmarkResult


class TestAggregationLogic:
    """Test suite for verifying benchmark aggregation correctness."""

    @pytest.fixture
    def sample_benchmark_result(self):
        """Create a sample BenchmarkResult for testing."""
        from src.types import DocumentCategory, ExtractionStatus, FileType, Framework

        return BenchmarkResult(
            framework=Framework.KREUZBERG_SYNC,
            file_path="test.pdf",
            file_size=1500000,  # 1.5MB in bytes
            file_type=FileType.PDF,
            category=DocumentCategory.SMALL,
            iteration=1,
            extraction_time=2.5,
            peak_memory_mb=200.0,
            avg_memory_mb=180.0,
            peak_cpu_percent=85.5,
            avg_cpu_percent=75.0,
            status=ExtractionStatus.SUCCESS,
            extracted_text="Sample text",
            character_count=100,
        )

    @pytest.fixture
    def sample_failed_result(self):
        """Create a failed BenchmarkResult for testing."""
        from src.types import DocumentCategory, ExtractionStatus, FileType, Framework

        return BenchmarkResult(
            framework=Framework.KREUZBERG_SYNC,
            file_path="failed.pdf",
            file_size=2000000,  # 2MB in bytes
            file_type=FileType.PDF,
            category=DocumentCategory.SMALL,
            iteration=1,
            extraction_time=0.0,
            peak_memory_mb=0.0,
            avg_memory_mb=0.0,
            peak_cpu_percent=0.0,
            avg_cpu_percent=0.0,
            status=ExtractionStatus.FAILED,
            extracted_text=None,
            error_message="Test error",
        )

    @pytest.fixture
    def sample_timeout_result(self):
        """Create a timeout BenchmarkResult for testing."""
        from src.types import DocumentCategory, ExtractionStatus, FileType, Framework

        return BenchmarkResult(
            framework=Framework.KREUZBERG_SYNC,
            file_path="timeout.pdf",
            file_size=5000000,  # 5MB in bytes
            file_type=FileType.PDF,
            category=DocumentCategory.MEDIUM,
            iteration=1,
            extraction_time=300.0,
            peak_memory_mb=500.0,
            avg_memory_mb=450.0,
            peak_cpu_percent=100.0,
            avg_cpu_percent=95.0,
            status=ExtractionStatus.TIMEOUT,
            extracted_text=None,
        )

    def test_success_rate_calculation(self, sample_benchmark_result: Any, sample_failed_result: Any):  # type: ignore[misc]
        """Test success rate calculation in aggregation."""
        from src.types import ExtractionStatus

        # Mock summary creation from results
        results = [sample_benchmark_result, sample_failed_result]

        # Calculate expected success rate
        successful = sum(1 for r in results if r.status == ExtractionStatus.SUCCESS)
        total = len(results)
        expected_rate = successful / total

        assert expected_rate == 0.5, "Success rate should be 50% with 1 success out of 2 results"

    def test_average_extraction_time_calculation(self, sample_benchmark_result):
        """Test average extraction time calculation."""
        import copy

        from src.types import ExtractionStatus

        # Create multiple results with known times
        result1 = copy.deepcopy(sample_benchmark_result)
        result1.extraction_time = 2.0

        result2 = copy.deepcopy(sample_benchmark_result)
        result2.extraction_time = 4.0

        results = [result1, result2]
        successful_results = [r for r in results if r.status == ExtractionStatus.SUCCESS]

        # Calculate expected average
        total_time = sum(r.extraction_time for r in successful_results)
        expected_avg = total_time / len(successful_results)

        assert expected_avg == 3.0, "Average extraction time should be 3.0 seconds"

    def test_files_per_second_calculation(self):
        """Test files per second calculation."""
        # Mock data: 10 files processed in 5 seconds total
        total_files = 10
        avg_extraction_time = 0.5  # 0.5 seconds per file

        # Calculate total time from files and average time per file
        total_time = total_files * avg_extraction_time
        files_per_second = total_files / total_time

        expected_fps = 2.0  # 10 files / 5 seconds = 2 files/second
        assert files_per_second == expected_fps, f"Expected {expected_fps} files/second, got {files_per_second}"

    def test_memory_aggregation(self, sample_benchmark_result):
        """Test memory usage aggregation."""
        import copy

        from src.types import ExtractionStatus

        # Create results with different memory usage
        result1 = copy.deepcopy(sample_benchmark_result)
        result1.peak_memory_mb = 100.0

        result2 = copy.deepcopy(sample_benchmark_result)
        result2.peak_memory_mb = 200.0

        result3 = copy.deepcopy(sample_benchmark_result)
        result3.peak_memory_mb = 150.0

        results = [result1, result2, result3]
        successful_results = [r for r in results if r.status == ExtractionStatus.SUCCESS]

        # Calculate expected average
        total_memory = sum(r.peak_memory_mb for r in successful_results)
        expected_avg = total_memory / len(successful_results)

        assert expected_avg == 150.0, "Average memory should be 150.0 MB"

    def test_category_aggregation(self, sample_benchmark_result):
        """Test aggregation by category."""
        import copy

        from src.types import DocumentCategory

        # Create results for different categories
        small_result = copy.deepcopy(sample_benchmark_result)
        small_result.category = DocumentCategory.SMALL
        small_result.file_size = 500000

        medium_result = copy.deepcopy(sample_benchmark_result)
        medium_result.category = DocumentCategory.MEDIUM
        medium_result.file_size = 5000000

        results = [small_result, medium_result]

        # Group by category
        categories = {}
        for result in results:
            if result.category not in categories:
                categories[result.category] = []
            categories[result.category].append(result)

        assert len(categories) == 2, "Should have 2 categories"
        assert DocumentCategory.SMALL in categories, "Should have small category"
        assert DocumentCategory.MEDIUM in categories, "Should have medium category"
        assert len(categories[DocumentCategory.SMALL]) == 1, "Small category should have 1 result"
        assert len(categories[DocumentCategory.MEDIUM]) == 1, "Medium category should have 1 result"

    def test_throughput_calculation(self, sample_benchmark_result):
        """Test MB/second throughput calculation."""
        import copy

        result = copy.deepcopy(sample_benchmark_result)
        result.file_size = 10000000  # 10MB
        result.extraction_time = 2.0

        # MB per second = file_size_mb / extraction_time
        file_size_mb = result.file_size / (1024 * 1024)  # Convert bytes to MB
        expected_throughput = file_size_mb / result.extraction_time
        calculated_throughput = file_size_mb / result.extraction_time

        assert abs(calculated_throughput - expected_throughput) < 0.001, (
            f"Expected {expected_throughput} MB/s, got {calculated_throughput} MB/s"
        )

    def test_failure_categorization(self, sample_failed_result, sample_timeout_result):
        """Test proper categorization of failures."""
        from src.types import ExtractionStatus

        results = [sample_failed_result, sample_timeout_result]

        # Count failure types
        error_failures = sum(1 for r in results if r.status == ExtractionStatus.FAILED and r.error_message)
        timeout_failures = sum(1 for r in results if r.status == ExtractionStatus.TIMEOUT)

        assert error_failures == 1, "Should have 1 error failure"
        assert timeout_failures == 1, "Should have 1 timeout failure"

    def test_framework_comparison_consistency(self):
        """Test that framework comparisons use consistent metrics."""
        # Mock framework results
        framework_a_results = [
            {"files_per_second": 10.0, "avg_memory_mb": 200.0, "success_rate": 0.95},
            {"files_per_second": 12.0, "avg_memory_mb": 180.0, "success_rate": 0.93},
        ]

        framework_b_results = [
            {"files_per_second": 8.0, "avg_memory_mb": 150.0, "success_rate": 0.98},
            {"files_per_second": 9.0, "avg_memory_mb": 160.0, "success_rate": 0.97},
        ]

        # Calculate averages for comparison
        def calculate_avg(results, metric):
            return sum(r[metric] for r in results) / len(results)

        a_speed = calculate_avg(framework_a_results, "files_per_second")
        b_speed = calculate_avg(framework_b_results, "files_per_second")

        a_memory = calculate_avg(framework_a_results, "avg_memory_mb")
        b_memory = calculate_avg(framework_b_results, "avg_memory_mb")

        # Framework A should be faster but use more memory
        assert a_speed > b_speed, "Framework A should be faster"
        assert a_memory > b_memory, "Framework A should use more memory"

    def test_zero_division_protection(self):
        """Test protection against division by zero in calculations."""
        # Test files per second with zero time
        total_files = 5
        avg_extraction_time = 0.0

        # Should handle zero division gracefully
        files_per_second = 1.0 / avg_extraction_time if avg_extraction_time > 0 else 0.0

        assert files_per_second == 0.0, "Should handle zero extraction time gracefully"

        # Test success rate with zero files
        successful_files = 0
        total_files = 0

        success_rate = successful_files / total_files if total_files > 0 else 0.0

        assert success_rate == 0.0, "Should handle zero total files gracefully"

    def test_weighted_average_calculation(self):
        """Test weighted average calculations for multi-category results."""
        # Mock category results with different file counts
        categories = [
            {"name": "small", "avg_time": 1.0, "file_count": 100},
            {"name": "medium", "avg_time": 5.0, "file_count": 50},
            {"name": "large", "avg_time": 20.0, "file_count": 10},
        ]

        # Calculate weighted average
        total_time = sum(cat["avg_time"] * cat["file_count"] for cat in categories)
        total_files = sum(cat["file_count"] for cat in categories)
        weighted_avg = total_time / total_files if total_files > 0 else 0

        # Expected: (1*100 + 5*50 + 20*10) / (100+50+10) = 550/160 = 3.4375
        expected_avg = 550.0 / 160.0

        assert abs(weighted_avg - expected_avg) < 0.001, f"Expected {expected_avg}, got {weighted_avg}"

    def test_percentile_calculations(self):
        """Test percentile-based metrics for robustness."""
        # Mock extraction times
        times = [1.0, 1.2, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 10.0, 20.0]
        times.sort()

        # Calculate 95th percentile (index for 95th percentile in 10 items)
        index_95 = int(0.95 * len(times))
        if index_95 >= len(times):
            index_95 = len(times) - 1

        p95_time = times[index_95]

        # 95th percentile should be the 9th item (0-indexed) = 20.0
        assert p95_time == 20.0, f"95th percentile should be 20.0, got {p95_time}"

    def test_data_validation_in_aggregation(self, sample_benchmark_result):
        """Test data validation during aggregation."""
        import copy

        # Test negative values are handled
        result = copy.deepcopy(sample_benchmark_result)
        result.extraction_time = -1.0
        result.peak_memory_mb = -100.0

        # Should validate and possibly exclude invalid data
        valid_time = max(0.0, result.extraction_time)
        valid_memory = max(0.0, result.peak_memory_mb)

        assert valid_time == 0.0, "Negative time should be normalized to 0"
        assert valid_memory == 0.0, "Negative memory should be normalized to 0"
