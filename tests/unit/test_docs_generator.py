"""Tests for docs_generator module."""

from pathlib import Path
from unittest.mock import Mock, patch

import msgspec
import pytest

from src.docs_generator import DocsGenerator
from src.types import AggregatedResults, BenchmarkSummary


def test_docs_generator_init_default_paths() -> None:
    """Test initialization with default paths."""
    generator = DocsGenerator()

    assert generator.docs_dir == Path("docs")
    assert generator.results_dir == Path("docs/results")
    assert generator.assets_dir == Path("docs/results/assets")


def test_docs_generator_init_custom_paths(temp_dir: Path) -> None:
    """Test initialization with custom paths."""
    custom_docs = temp_dir / "custom_docs"
    generator = DocsGenerator(custom_docs)

    assert generator.docs_dir == custom_docs
    assert generator.results_dir == custom_docs / "results"
    assert generator.assets_dir == custom_docs / "results" / "assets"


def test_generate_from_results_creates_directories(aggregated_results: AggregatedResults, temp_dir: Path) -> None:
    """Test that generate_from_results creates necessary directories."""
    results_file = temp_dir / "results.json"
    with open(results_file, "w") as f:
        f.write(msgspec.json.encode(aggregated_results).decode())

    generator = DocsGenerator(temp_dir / "docs")
    generator.generate_from_results(results_file)

    assert (temp_dir / "docs" / "results").exists()
    assert (temp_dir / "docs" / "results" / "assets").exists()


def test_generate_from_results_creates_pages(aggregated_results: AggregatedResults, temp_dir: Path) -> None:
    """Test that all expected pages are created."""
    results_file = temp_dir / "results.json"
    with open(results_file, "w") as f:
        f.write(msgspec.json.encode(aggregated_results).decode())

    generator = DocsGenerator(temp_dir / "docs")
    generator.generate_from_results(results_file)

    assert (temp_dir / "docs" / "results" / "index.md").exists()

    perf_dir = temp_dir / "docs" / "results" / "performance"
    assert perf_dir.exists()
    assert (perf_dir / "speed.md").exists()
    assert (perf_dir / "memory.md").exists()

    formats_dir = temp_dir / "docs" / "results" / "formats"
    assert formats_dir.exists()
    assert (formats_dir / "index.md").exists()

    interactive_dir = temp_dir / "docs" / "results" / "interactive"
    assert interactive_dir.exists()
    assert (interactive_dir / "dashboard.md").exists()


def test_copy_charts(temp_dir: Path, charts_dir: Path) -> None:
    """Test copying chart files to docs assets."""
    generator = DocsGenerator(temp_dir / "docs")
    generator.assets_dir.mkdir(parents=True)

    generator._copy_charts(charts_dir)

    charts_dest = generator.assets_dir / "charts"
    assert charts_dest.exists()
    assert (charts_dest / "performance_comparison_large.png").exists()
    assert (charts_dest / "interactive_dashboard.html").exists()


def test_copy_charts_nonexistent_dir(temp_dir: Path) -> None:
    """Test copying charts when source directory doesn't exist."""
    generator = DocsGenerator(temp_dir / "docs")
    generator.assets_dir.mkdir(parents=True)

    generator._copy_charts(temp_dir / "nonexistent")


def test_calculate_framework_stats(aggregated_results: AggregatedResults) -> None:
    """Test framework statistics calculation."""
    generator = DocsGenerator()
    stats = generator._calculate_framework_stats(aggregated_results)

    assert isinstance(stats, dict)
    all_summaries = []
    for summaries_list in aggregated_results.framework_summaries.values():
        all_summaries.extend(summaries_list)
    frameworks = {s.framework.value if hasattr(s.framework, "value") else str(s.framework) for s in all_summaries}
    assert set(stats.keys()) == frameworks

    for fw_stats in stats.values():
        assert "total_files" in fw_stats
        assert "successful" in fw_stats
        assert "avg_speed" in fw_stats
        assert "avg_memory" in fw_stats
        assert "success_rate" in fw_stats


def test_generate_ranking_table(aggregated_results: AggregatedResults) -> None:
    """Test ranking table generation."""
    generator = DocsGenerator()
    stats = generator._calculate_framework_stats(aggregated_results)

    speed_table = generator._generate_ranking_table(stats, "speed")
    assert isinstance(speed_table, str)
    assert "**" in speed_table
    assert "|" in speed_table

    memory_table = generator._generate_ranking_table(stats, "memory")
    assert isinstance(memory_table, str)

    success_table = generator._generate_ranking_table(stats, "success")
    assert isinstance(success_table, str)


def test_generate_insights(aggregated_results: AggregatedResults) -> None:
    """Test insights generation."""
    generator = DocsGenerator()
    stats = generator._calculate_framework_stats(aggregated_results)

    insights = generator._generate_insights(stats)
    assert isinstance(insights, str)
    assert "Speed Champion" in insights
    assert "Memory Efficient" in insights
    assert "Most Reliable" in insights


def test_generate_format_table(aggregated_results: AggregatedResults) -> None:
    """Test format table generation."""
    generator = DocsGenerator()

    insights = generator._generate_category_format_insights(aggregated_results)
    assert isinstance(insights, str)
    assert len(insights) > 0


def test_results_index_content(aggregated_results: AggregatedResults, temp_dir: Path) -> None:
    """Test that results index contains expected content."""
    results_file = temp_dir / "results.json"
    with open(results_file, "w") as f:
        f.write(msgspec.json.encode(aggregated_results).decode())

    generator = DocsGenerator(temp_dir / "docs")
    generator.generate_from_results(results_file)

    index_file = temp_dir / "docs" / "results" / "index.md"
    content = index_file.read_text()

    assert "Latest Benchmark Results" in content
    assert "Performance Rankings" in content
    assert "By Speed" in content
    assert "By Memory Efficiency" in content
    assert "Key Insights" in content

    all_summaries = []
    for summaries_list in aggregated_results.framework_summaries.values():
        all_summaries.extend(summaries_list)
    frameworks = {s.framework.value if hasattr(s.framework, "value") else str(s.framework) for s in all_summaries}
    for framework in frameworks:
        assert framework in content


def test_performance_pages_content(aggregated_results: AggregatedResults, temp_dir: Path) -> None:
    """Test that performance pages contain expected content."""
    results_file = temp_dir / "results.json"
    with open(results_file, "w") as f:
        f.write(msgspec.json.encode(aggregated_results).decode())

    generator = DocsGenerator(temp_dir / "docs")
    generator.generate_from_results(results_file)

    speed_file = temp_dir / "docs" / "results" / "performance" / "speed.md"
    speed_content = speed_file.read_text()
    assert "Speed Performance Analysis" in speed_content
    assert "performance_comparison_large.png" in speed_content

    memory_file = temp_dir / "docs" / "results" / "performance" / "memory.md"
    memory_content = memory_file.read_text()
    assert "Memory Usage Analysis" in memory_content
    assert "resource_usage_heatmaps.png" in memory_content


def test_interactive_page_content(aggregated_results: AggregatedResults, temp_dir: Path) -> None:
    """Test that interactive page contains expected content."""
    results_file = temp_dir / "results.json"
    with open(results_file, "w") as f:
        f.write(msgspec.json.encode(aggregated_results).decode())

    generator = DocsGenerator(temp_dir / "docs")
    generator.generate_from_results(results_file)

    dashboard_file = temp_dir / "docs" / "results" / "interactive" / "dashboard.md"
    content = dashboard_file.read_text()

    assert "Interactive Dashboard" in content
    assert "iframe" in content
    assert "interactive_dashboard.html" in content
    assert "Raw Data Access" in content


@patch("src.docs_generator.DocsGenerator")
@patch("argparse.ArgumentParser")
def test_main_function_basic(mock_parser: Mock, mock_generator_class: Mock) -> None:
    """Test main function with basic arguments."""
    mock_args = Mock()
    mock_args.results_file = Path("results.json")
    mock_args.charts_dir = None
    mock_args.docs_dir = Path("docs")

    mock_parser.return_value.parse_args.return_value = mock_args
    mock_generator = Mock()
    mock_generator_class.return_value = mock_generator

    from src.docs_generator import main

    main()

    mock_generator_class.assert_called_once_with(Path("docs"))
    mock_generator.generate_from_results.assert_called_once_with(Path("results.json"), None)


@patch("src.docs_generator.DocsGenerator")
@patch("argparse.ArgumentParser")
def test_main_function_with_charts(mock_parser: Mock, mock_generator_class: Mock) -> None:
    """Test main function with charts directory."""
    mock_args = Mock()
    mock_args.results_file = Path("results.json")
    mock_args.charts_dir = Path("charts")
    mock_args.docs_dir = Path("custom_docs")

    mock_parser.return_value.parse_args.return_value = mock_args
    mock_generator = Mock()
    mock_generator_class.return_value = mock_generator

    from src.docs_generator import main

    main()

    mock_generator_class.assert_called_once_with(Path("custom_docs"))
    mock_generator.generate_from_results.assert_called_once_with(Path("results.json"), Path("charts"))


def test_empty_results(temp_dir: Path) -> None:
    """Test handling of empty results."""
    empty_results = AggregatedResults(
        total_runs=0,
        total_files_processed=0,
        total_time_seconds=0.0,
        framework_summaries={},
        category_summaries={},
        framework_category_matrix={},
        failure_patterns={},
        timeout_files=[],
        performance_over_iterations={},
        platform_results={},
    )

    results_file = temp_dir / "results.json"
    with open(results_file, "w") as f:
        f.write(msgspec.json.encode(empty_results).decode())

    generator = DocsGenerator(temp_dir / "docs")
    generator.generate_from_results(results_file)

    assert (temp_dir / "docs" / "results" / "index.md").exists()


def test_missing_results_file(temp_dir: Path) -> None:
    """Test handling of missing results file."""
    generator = DocsGenerator(temp_dir / "docs")

    with pytest.raises(FileNotFoundError):
        generator.generate_from_results(temp_dir / "nonexistent.json")


def test_malformed_results_file(temp_dir: Path) -> None:
    """Test handling of malformed results file."""
    results_file = temp_dir / "results.json"
    results_file.write_text("invalid json content")

    generator = DocsGenerator(temp_dir / "docs")

    with pytest.raises(Exception):
        generator.generate_from_results(results_file)


def test_framework_stats_with_missing_data() -> None:
    """Test framework stats calculation with missing data."""
    from src.types import DocumentCategory, Framework

    summary = BenchmarkSummary(
        framework=Framework.KREUZBERG_SYNC,
        category=DocumentCategory.SMALL,
        total_files=1,
        successful_files=1,
        failed_files=0,
        partial_files=0,
        timeout_files=0,
        success_rate=100.0,
        avg_extraction_time=None,
        median_extraction_time=0.5,
        avg_peak_memory_mb=None,
        avg_cpu_percent=25.0,
        files_per_second=None,
        mb_per_second=1.0,
    )

    results = AggregatedResults(
        total_runs=1,
        total_files_processed=1,
        total_time_seconds=1.0,
        framework_summaries={Framework.KREUZBERG_SYNC: [summary]},
        category_summaries={DocumentCategory.SMALL: [summary]},
        framework_category_matrix={"kreuzberg_sync_small": summary},
        failure_patterns={},
        timeout_files=[],
        performance_over_iterations={Framework.KREUZBERG_SYNC: [1.0]},
        platform_results={},
    )

    generator = DocsGenerator()
    stats = generator._calculate_framework_stats(results)

    assert "kreuzberg_sync" in stats
    assert stats["kreuzberg_sync"]["avg_speed"] == 0
    assert stats["kreuzberg_sync"]["avg_memory"] == 0
