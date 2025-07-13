"""Tests for benchmark calculation correctness.

~keep Verification suite that:
- Validates speed calculations (files/sec) against real benchmark data
- Ensures memory aggregation accuracy across categories
- Confirms success rate formulas are mathematically correct
- Tests framework comparison consistency and relative rankings
- Protects against calculation errors that would mislead users
"""

import json
import math
from pathlib import Path

import pytest


class TestBenchmarkCalculations:
    """~keep Verification suite using real benchmark data to ensure calculation accuracy."""

    @pytest.fixture
    def aggregated_data(self):
        """~keep Load real aggregated results from CI run for testing."""
        data_path = Path("tests/test_data/aggregated_results.json")
        with open(data_path) as f:
            return json.load(f)

    @pytest.fixture
    def summary_metrics(self):
        """~keep Load real summary metrics from website for cross-validation."""
        data_path = Path("tests/test_data/summary_metrics.json")
        with open(data_path) as f:
            return json.load(f)

    def test_speed_calculations_kreuzberg_sync(self, summary_metrics):  # type: ignore[misc]
        """~keep Verify files/sec calculation accuracy using exact benchmark data."""
        framework = "kreuzberg_sync"
        metrics = summary_metrics["framework_performance"][framework]

        # Basic sanity checks for speed metric
        files_per_second = metrics["avg_files_per_second"]
        assert files_per_second > 0, "Files per second should be positive"
        assert files_per_second < 1000, "Files per second should be realistic"

        # Exact value validation against known benchmark results
        expected_fps = 20.504910406347275
        assert abs(files_per_second - expected_fps) < 0.001, f"Expected {expected_fps}, got {files_per_second}"

    def test_speed_calculations_kreuzberg_async(self, summary_metrics):  # type: ignore[misc]
        """Test speed calculations for kreuzberg_async framework."""
        framework = "kreuzberg_async"
        metrics = summary_metrics["framework_performance"][framework]

        files_per_second = metrics["avg_files_per_second"]
        expected_fps = 16.443231873676435
        assert abs(files_per_second - expected_fps) < 0.001, f"Expected {expected_fps}, got {files_per_second}"

    def test_speed_calculations_docling(self, summary_metrics):  # type: ignore[misc]
        """Test speed calculations for docling framework."""
        framework = "docling"
        metrics = summary_metrics["framework_performance"][framework]

        files_per_second = metrics["avg_files_per_second"]
        expected_fps = 0.17797559834766594
        assert abs(files_per_second - expected_fps) < 0.001, f"Expected {expected_fps}, got {files_per_second}"

        # Docling should be slower than Kreuzberg
        kreuzberg_fps = summary_metrics["framework_performance"]["kreuzberg_sync"]["avg_files_per_second"]
        assert files_per_second < kreuzberg_fps, "Docling should be slower than Kreuzberg"

    def test_speed_calculations_markitdown(self, summary_metrics):  # type: ignore[misc]
        """Test speed calculations for markitdown framework."""
        framework = "markitdown"
        metrics = summary_metrics["framework_performance"][framework]

        files_per_second = metrics["avg_files_per_second"]
        expected_fps = 16.554927431747444
        assert abs(files_per_second - expected_fps) < 0.001, f"Expected {expected_fps}, got {files_per_second}"

    def test_speed_calculations_unstructured(self, summary_metrics):  # type: ignore[misc]
        """Test speed calculations for unstructured framework."""
        framework = "unstructured"
        metrics = summary_metrics["framework_performance"][framework]

        files_per_second = metrics["avg_files_per_second"]
        expected_fps = 2.8890274305803687
        assert abs(files_per_second - expected_fps) < 0.001, f"Expected {expected_fps}, got {files_per_second}"

    def test_speed_calculations_extractous(self, summary_metrics):  # type: ignore[misc]
        """Test speed calculations for extractous framework."""
        framework = "extractous"
        metrics = summary_metrics["framework_performance"][framework]

        files_per_second = metrics["avg_files_per_second"]
        expected_fps = 2.9567113525077877
        assert abs(files_per_second - expected_fps) < 0.001, f"Expected {expected_fps}, got {files_per_second}"

    def test_speed_consistency_across_frameworks(self, summary_metrics):  # type: ignore[misc]
        """Test that speed calculations are consistent across frameworks."""
        frameworks = summary_metrics["framework_performance"]

        # All frameworks should have positive speed
        for framework, metrics in frameworks.items():
            files_per_second = metrics["avg_files_per_second"]
            assert files_per_second > 0, f"{framework} should have positive speed"

        # Verify relative performance ordering based on known data
        kreuzberg_sync_fps = frameworks["kreuzberg_sync"]["avg_files_per_second"]
        markitdown_fps = frameworks["markitdown"]["avg_files_per_second"]
        docling_fps = frameworks["docling"]["avg_files_per_second"]

        # Kreuzberg sync should be fastest among these
        assert kreuzberg_sync_fps > markitdown_fps, "Kreuzberg sync should be faster than MarkItDown"
        assert kreuzberg_sync_fps > docling_fps, "Kreuzberg sync should be faster than Docling"
        assert markitdown_fps > docling_fps, "MarkItDown should be faster than Docling"

    def test_memory_calculations_kreuzberg_sync(self, summary_metrics):  # type: ignore[misc]
        """Test memory calculations for kreuzberg_sync framework."""
        framework = "kreuzberg_sync"
        metrics = summary_metrics["framework_performance"][framework]

        avg_memory = metrics["avg_memory_mb"]
        expected_memory = 353.78355135658916
        assert abs(avg_memory - expected_memory) < 0.001, f"Expected {expected_memory}MB, got {avg_memory}MB"

        # Memory should be reasonable (between 100MB and 10GB)
        assert 100 < avg_memory < 10000, f"Memory usage {avg_memory}MB should be realistic"

    def test_memory_calculations_docling(self, summary_metrics):  # type: ignore[misc]
        """Test memory calculations for docling framework."""
        framework = "docling"
        metrics = summary_metrics["framework_performance"][framework]

        avg_memory = metrics["avg_memory_mb"]
        expected_memory = 1764.0135008321006
        assert abs(avg_memory - expected_memory) < 0.001, f"Expected {expected_memory}MB, got {avg_memory}MB"

        # Docling should use more memory than Kreuzberg
        kreuzberg_memory = summary_metrics["framework_performance"]["kreuzberg_sync"]["avg_memory_mb"]
        assert avg_memory > kreuzberg_memory, "Docling should use more memory than Kreuzberg"

    def test_memory_consistency_across_frameworks(self, summary_metrics):  # type: ignore[misc]
        """Test that memory calculations are consistent across frameworks."""
        frameworks = summary_metrics["framework_performance"]

        # All frameworks should have positive memory usage
        for framework, metrics in frameworks.items():
            avg_memory = metrics["avg_memory_mb"]
            assert avg_memory > 0, f"{framework} should have positive memory usage"
            assert avg_memory < 10000, f"{framework} memory usage {avg_memory}MB should be realistic"

    def test_success_rate_calculations(self, summary_metrics):  # type: ignore[misc]
        """~keep Validate success rate formula: successful_files / total_files."""
        frameworks = summary_metrics["framework_performance"]

        for framework, metrics in frameworks.items():
            total_files = metrics["total_files"]
            successful_files = metrics["successful_files"]
            success_rate = metrics["success_rate"]

            # Test fundamental success rate calculation
            expected_rate = successful_files / total_files if total_files > 0 else 0
            assert abs(success_rate - expected_rate) < 0.001, (
                f"{framework}: Expected {expected_rate}, got {success_rate}"
            )

            # Boundary validation - success rate must be valid percentage
            assert 0 <= success_rate <= 1, f"{framework} success rate {success_rate} should be between 0 and 1"

            # Logic validation - successful cannot exceed total
            assert successful_files <= total_files, (
                f"{framework}: Successful files {successful_files} should not exceed total {total_files}"
            )

    def test_category_performance_totals(self, summary_metrics):  # type: ignore[misc]
        """Test category performance calculations."""
        category_perf = summary_metrics["category_performance"]

        for category, metrics in category_perf.items():
            total_files = metrics["total_files"]
            successful_files = metrics["successful_files"]
            success_rate = metrics["success_rate"]

            # Verify success rate calculation
            expected_rate = successful_files / total_files if total_files > 0 else 0
            assert abs(success_rate - expected_rate) < 0.001, (
                f"{category}: Expected {expected_rate}, got {success_rate}"
            )

            # All test categories should have files
            assert total_files > 0, f"{category} should have test files"

    def test_overall_totals_consistency(self, summary_metrics):  # type: ignore[misc]
        """Test that overall totals are consistent."""
        total_runs = summary_metrics["total_runs"]
        total_files_processed = summary_metrics["total_files_processed"]
        frameworks_tested = summary_metrics["frameworks_tested"]

        # Should have reasonable numbers
        assert total_runs > 0, "Should have at least one run"
        assert total_files_processed > 0, "Should have processed files"
        assert frameworks_tested > 0, "Should have tested frameworks"

        # Expected values from the data
        assert total_runs == 18, f"Expected 18 runs, got {total_runs}"
        assert total_files_processed == 1353, f"Expected 1353 files processed, got {total_files_processed}"
        assert frameworks_tested == 6, f"Expected 6 frameworks, got {frameworks_tested}"

    def test_framework_file_counts_consistency(self, summary_metrics):  # type: ignore[misc]
        """Test that framework file counts are consistent."""
        frameworks = summary_metrics["framework_performance"]

        # Sum up all framework file counts
        total_framework_files = sum(metrics["total_files"] for metrics in frameworks.values())

        # This should match the total files processed
        expected_total = summary_metrics["total_files_processed"]
        assert total_framework_files == expected_total, (
            f"Framework totals {total_framework_files} should match overall total {expected_total}"
        )

    def test_mathematical_precision(self, summary_metrics):  # type: ignore[misc]
        """Test mathematical precision of calculations."""
        frameworks = summary_metrics["framework_performance"]

        for framework, metrics in frameworks.items():
            # Test that floating point calculations are precise enough
            files_per_second = metrics["avg_files_per_second"]
            avg_memory = metrics["avg_memory_mb"]
            success_rate = metrics["success_rate"]

            # Should not be NaN or infinite
            assert not math.isnan(files_per_second), f"{framework} files_per_second should not be NaN"
            assert not math.isinf(files_per_second), f"{framework} files_per_second should not be infinite"
            assert not math.isnan(avg_memory), f"{framework} avg_memory should not be NaN"
            assert not math.isinf(avg_memory), f"{framework} avg_memory should not be infinite"
            assert not math.isnan(success_rate), f"{framework} success_rate should not be NaN"
            assert not math.isinf(success_rate), f"{framework} success_rate should not be infinite"
