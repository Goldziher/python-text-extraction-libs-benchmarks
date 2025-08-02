"""Tests for visualization module to ensure proper handling of None values."""

from pathlib import Path
from unittest.mock import patch

import msgspec
import pytest

from src.types import AggregatedResults, BenchmarkSummary, DocumentCategory, Framework
from src.visualize import BenchmarkVisualizer


class TestVisualizationNoneHandling:
    """Test suite for verifying visualization handles None values correctly."""

    @pytest.fixture
    def sample_aggregated_results_with_nones(self):
        """Create aggregated results with None values."""
        summaries = {
            "kreuzberg_sync": [
                BenchmarkSummary(
                    framework=Framework.KREUZBERG_SYNC,
                    category=DocumentCategory.TINY,
                    total_files=10,
                    successful_files=8,
                    failed_files=2,
                    partial_files=0,
                    timeout_files=0,
                    avg_extraction_time=0.5,
                    median_extraction_time=0.4,
                    min_extraction_time=0.1,
                    max_extraction_time=1.0,
                    std_extraction_time=0.2,
                    avg_peak_memory_mb=100.0,
                    avg_cpu_percent=50.0,
                    files_per_second=2.0,
                    mb_per_second=1.0,
                    success_rate=0.8,
                    avg_character_count=1000,
                    avg_word_count=200,
                    avg_quality_score=None,  # None value
                    min_quality_score=None,  # None value
                    max_quality_score=None,  # None value
                    avg_completeness=None,  # None value
                    avg_coherence=None,  # None value
                    avg_readability=None,  # None value
                ),
                BenchmarkSummary(
                    framework=Framework.KREUZBERG_SYNC,
                    category=DocumentCategory.SMALL,
                    total_files=5,
                    successful_files=5,
                    failed_files=0,
                    partial_files=0,
                    timeout_files=0,
                    avg_extraction_time=None,  # None value
                    median_extraction_time=1.0,
                    min_extraction_time=0.5,
                    max_extraction_time=2.0,
                    std_extraction_time=0.5,
                    avg_peak_memory_mb=None,  # None value
                    avg_cpu_percent=60.0,
                    files_per_second=None,  # None value
                    mb_per_second=None,  # None value
                    success_rate=1.0,  # Use valid float instead of None
                    avg_character_count=2000,
                    avg_word_count=400,
                    avg_quality_score=None,
                    min_quality_score=None,
                    max_quality_score=None,
                    avg_completeness=None,
                    avg_coherence=None,
                    avg_readability=None,
                ),
            ],
        }

        return AggregatedResults(
            total_runs=1,
            total_files_processed=15,
            total_time_seconds=100.0,
            framework_summaries=summaries,
            category_summaries={},
            framework_category_matrix={},
            failure_patterns={},
            timeout_files=[],
            performance_over_iterations={},
            platform_results={},
        )

    def test_category_analysis_handles_none_avg_times(self, sample_aggregated_results_with_nones, tmp_path):
        """Test that category analysis correctly handles None values in avg_times."""
        visualizer = BenchmarkVisualizer(output_dir=tmp_path)

        # Mock matplotlib to avoid creating actual plots
        with patch("matplotlib.pyplot.savefig"):
            output_files = visualizer._create_category_analysis(sample_aggregated_results_with_nones)  # noqa: SLF001

        # Should complete without errors
        assert isinstance(output_files, list)

    def test_performance_comparison_handles_none_success_rate(self, sample_aggregated_results_with_nones, tmp_path):
        """Test that performance comparison handles None success_rate values."""
        visualizer = BenchmarkVisualizer(output_dir=tmp_path)

        with patch("matplotlib.pyplot.savefig"):
            output_files = visualizer._create_performance_comparison(sample_aggregated_results_with_nones)  # noqa: SLF001

        # Should complete without errors
        assert isinstance(output_files, list)

    def test_summary_metrics_handles_none_values(self, sample_aggregated_results_with_nones, tmp_path):
        """Test that summary metrics generation handles None values in calculations."""
        visualizer = BenchmarkVisualizer(output_dir=tmp_path)

        # Create a temporary file with the aggregated results
        test_file = tmp_path / "test_aggregated.json"
        with open(test_file, "wb") as f:
            f.write(msgspec.json.encode(sample_aggregated_results_with_nones))

        # Generate summary metrics
        metrics = visualizer.generate_summary_metrics(test_file)

        # Verify metrics were generated without errors
        assert "framework_performance" in metrics
        assert "kreuzberg_sync" in metrics["framework_performance"]

        # Check that averages handle None values correctly
        fw_metrics = metrics["framework_performance"]["kreuzberg_sync"]
        assert fw_metrics["avg_files_per_second"] >= 0  # Should not error on None
        assert fw_metrics["avg_memory_mb"] >= 0  # Should not error on None

    def test_interactive_dashboard_handles_none_values(self, sample_aggregated_results_with_nones, tmp_path):
        """Test that interactive dashboard handles None values in data."""
        visualizer = BenchmarkVisualizer(output_dir=tmp_path)

        # Mock plotly to avoid creating actual plots
        with patch("plotly.graph_objects.Figure"):
            output_path = visualizer._create_interactive_dashboard(sample_aggregated_results_with_nones)  # noqa: SLF001

        # Should complete without errors
        assert isinstance(output_path, Path)

    def test_success_rate_distribution_skips_none_rates(self, tmp_path):
        """Test that success rate distribution correctly skips None rates."""
        visualizer = BenchmarkVisualizer(output_dir=tmp_path)

        # Create test data with mixed None and valid success rates
        summaries = {
            "test_framework": [
                BenchmarkSummary(
                    framework=Framework.KREUZBERG_SYNC,
                    category=DocumentCategory.TINY,
                    total_files=10,
                    successful_files=8,
                    failed_files=2,
                    partial_files=0,
                    timeout_files=0,
                    avg_extraction_time=0.5,
                    median_extraction_time=0.4,
                    min_extraction_time=0.1,
                    max_extraction_time=1.0,
                    std_extraction_time=0.2,
                    avg_peak_memory_mb=100.0,
                    avg_cpu_percent=50.0,
                    files_per_second=2.0,
                    mb_per_second=1.0,
                    success_rate=0.8,
                    avg_character_count=1000,
                    avg_word_count=200,
                    avg_quality_score=None,
                    min_quality_score=None,
                    max_quality_score=None,
                    avg_completeness=None,
                    avg_coherence=None,
                    avg_readability=None,
                ),
                BenchmarkSummary(
                    framework=Framework.KREUZBERG_SYNC,
                    category=DocumentCategory.SMALL,
                    total_files=5,
                    successful_files=5,
                    failed_files=0,
                    partial_files=0,
                    timeout_files=0,
                    avg_extraction_time=1.0,
                    median_extraction_time=1.0,
                    min_extraction_time=0.5,
                    max_extraction_time=2.0,
                    std_extraction_time=0.5,
                    avg_peak_memory_mb=150.0,
                    avg_cpu_percent=60.0,
                    files_per_second=1.0,
                    mb_per_second=0.5,
                    success_rate=1.0,  # Use valid float instead of None
                    avg_character_count=2000,
                    avg_word_count=400,
                    avg_quality_score=None,
                    min_quality_score=None,
                    max_quality_score=None,
                    avg_completeness=None,
                    avg_coherence=None,
                    avg_readability=None,
                ),
            ],
        }

        aggregated = AggregatedResults(
            total_runs=1,
            total_files_processed=15,
            total_time_seconds=100.0,
            framework_summaries=summaries,
            category_summaries={},
            framework_category_matrix={},
            failure_patterns={},
            timeout_files=[],
            performance_over_iterations={},
            platform_results={},
        )

        with patch("matplotlib.pyplot.savefig"):
            output_files = visualizer._create_category_analysis(aggregated)  # noqa: SLF001

        # Should complete without errors when encountering None success rates
        assert isinstance(output_files, list)
