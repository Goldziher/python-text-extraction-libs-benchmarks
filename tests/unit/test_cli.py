"""Tests for CLI module."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from src.cli import main


def test_cli_main_help() -> None:
    """Test that main CLI shows help."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "benchmark" in result.output
    assert "report" in result.output
    assert "visualize" in result.output


def test_benchmark_command_help() -> None:
    """Test benchmark command help."""
    runner = CliRunner()
    result = runner.invoke(main, ["benchmark", "--help"])

    assert result.exit_code == 0
    assert "Run comprehensive benchmarks" in result.output
    assert "--framework" in result.output
    assert "--category" in result.output


def test_report_command_help() -> None:
    """Test report command help."""
    runner = CliRunner()
    result = runner.invoke(main, ["report", "--help"])

    assert result.exit_code == 0
    assert "Generate reports from aggregated benchmark results" in result.output
    assert "--format" in result.output


def test_visualize_command_help() -> None:
    """Test visualize command help."""
    runner = CliRunner()
    result = runner.invoke(main, ["visualize", "--help"])

    assert result.exit_code == 0
    assert "Generate comprehensive visualizations" in result.output


def test_aggregate_command_help() -> None:
    """Test aggregate command help."""
    runner = CliRunner()
    result = runner.invoke(main, ["aggregate", "--help"])

    assert result.exit_code == 0
    assert "Aggregate results from multiple benchmark runs" in result.output


def test_list_frameworks_command() -> None:
    """Test list-frameworks command."""
    runner = CliRunner()
    result = runner.invoke(main, ["list-frameworks"])

    assert result.exit_code == 0
    assert "kreuzberg" in result.output.lower()


def test_list_frameworks_json() -> None:
    """Test list-frameworks with JSON output."""
    runner = CliRunner()
    result = runner.invoke(main, ["list-frameworks", "--json"])

    assert result.exit_code == 0
    import json

    try:
        json.loads(result.output)
    except json.JSONDecodeError:
        pytest.fail("Output should be valid JSON")


@patch("src.cli.BenchmarkEngine")
def test_benchmark_command_execution(mock_engine: Mock) -> None:
    """Test benchmark command execution."""
    mock_instance = Mock()
    mock_engine.return_value = mock_instance
    mock_instance.run_benchmarks.return_value = []

    runner = CliRunner()
    with runner.isolated_filesystem():
        test_docs = Path("test_documents")
        test_docs.mkdir()
        (test_docs / "test.txt").write_text("test content")

        result = runner.invoke(
            main,
            [
                "benchmark",
                "--framework",
                "kreuzberg_sync",
                "--category",
                "small",
                "--iterations",
                "1",
                "--timeout",
                "60",
            ],
        )

        assert result.exit_code == 0
        mock_engine.assert_called_once()


@patch("src.cli.DocsGenerator")
def test_report_command_execution(mock_docs_gen: Mock) -> None:
    """Test report command execution."""
    mock_generator = Mock()
    mock_docs_gen.return_value = mock_generator

    runner = CliRunner()
    with runner.isolated_filesystem():
        results_dir = Path("results")
        results_dir.mkdir()
        aggregated_file = results_dir / "aggregated_results.json"
        aggregated_file.write_text('{"summaries": [], "results": []}')

        result = runner.invoke(main, ["report", "--output-format", "markdown"])

        assert result.exit_code == 0
        mock_docs_gen.assert_called_once()


@patch("src.cli.DocsGenerator")
def test_report_command_with_custom_file(mock_docs_gen: Mock) -> None:
    """Test report command with custom aggregated file."""
    mock_generator = Mock()
    mock_docs_gen.return_value = mock_generator

    runner = CliRunner()
    with runner.isolated_filesystem():
        custom_file = Path("custom_results.json")
        custom_file.write_text('{"summaries": [], "results": []}')

        result = runner.invoke(main, ["report", "--aggregated-file", str(custom_file), "--output-format", "markdown"])

        assert result.exit_code == 0
        mock_docs_gen.assert_called_once()


@patch("src.cli.VisualizationAnalyzer")
def test_visualize_command_execution(mock_viz: Mock) -> None:
    """Test visualize command execution."""
    mock_analyzer = Mock()
    mock_viz.return_value = mock_analyzer

    runner = CliRunner()
    with runner.isolated_filesystem():
        results_dir = Path("results")
        results_dir.mkdir()
        aggregated_file = results_dir / "aggregated_results.json"
        aggregated_file.write_text('{"summaries": [], "results": []}')

        result = runner.invoke(main, ["visualize"])

        assert result.exit_code == 0
        mock_viz.assert_called_once()


def test_aggregate_command_execution() -> None:
    """Test aggregate command execution."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        input_dir1 = Path("run1")
        input_dir1.mkdir()
        (input_dir1 / "results.json").write_text("[]")

        input_dir2 = Path("run2")
        input_dir2.mkdir()
        (input_dir2 / "results.json").write_text("[]")

        result = runner.invoke(main, ["aggregate", str(input_dir1), str(input_dir2), "--output-dir", "aggregated"])

        assert result.exit_code in [0, 1]


def test_benchmark_command_with_invalid_framework() -> None:
    """Test benchmark command with invalid framework."""
    runner = CliRunner()
    result = runner.invoke(main, ["benchmark", "--framework", "nonexistent_framework"])

    assert result.exit_code != 0
    assert "Invalid value" in result.output or "not supported" in result.output


def test_benchmark_command_with_invalid_category() -> None:
    """Test benchmark command with invalid category."""
    runner = CliRunner()
    result = runner.invoke(main, ["benchmark", "--category", "nonexistent_category"])

    assert result.exit_code != 0
    assert "Invalid value" in result.output or "not supported" in result.output


def test_report_command_missing_results() -> None:
    """Test report command when no results exist."""
    runner = CliRunner()
    result = runner.invoke(main, ["report"])

    assert result.exit_code != 0 or "No aggregated results" in result.output


def test_visualize_command_missing_results() -> None:
    """Test visualize command when no results exist."""
    runner = CliRunner()
    result = runner.invoke(main, ["visualize"])

    assert result.exit_code != 0 or "No aggregated results" in result.output


@patch("src.cli.Path")
def test_benchmark_missing_test_documents(mock_path: Mock) -> None:
    """Test benchmark command when test_documents directory is missing."""
    mock_path_instance = Mock()
    mock_path_instance.exists.return_value = False
    mock_path.return_value = mock_path_instance

    runner = CliRunner()
    result = runner.invoke(main, ["benchmark"])

    assert result.exit_code != 0


def test_list_categories_command() -> None:
    """Test list-categories command."""
    runner = CliRunner()
    result = runner.invoke(main, ["list-categories"])

    assert result.exit_code == 0
    assert "small" in result.output.lower()
    assert "medium" in result.output.lower()


def test_list_file_types_command() -> None:
    """Test list-file-types command."""
    runner = CliRunner()
    result = runner.invoke(main, ["list-file-types"])

    assert result.exit_code == 0
    assert "pdf" in result.output.lower()
    assert "docx" in result.output.lower()


def test_installation_sizes_command() -> None:
    """Test installation-sizes command."""
    runner = CliRunner()
    result = runner.invoke(main, ["installation-sizes"])

    assert result.exit_code == 0
    assert "kreuzberg" in result.output.lower()


@patch("src.cli.BenchmarkEngine")
def test_benchmark_with_all_options(mock_engine: Mock) -> None:
    """Test benchmark command with all options."""
    mock_instance = Mock()
    mock_engine.return_value = mock_instance
    mock_instance.run_benchmarks.return_value = []

    runner = CliRunner()
    with runner.isolated_filesystem():
        test_docs = Path("test_documents")
        test_docs.mkdir()
        (test_docs / "test.pdf").write_bytes(b"dummy pdf content")

        result = runner.invoke(
            main,
            [
                "benchmark",
                "--framework",
                "kreuzberg_sync,extractous",
                "--category",
                "small,medium",
                "--file-type",
                "pdf,docx",
                "--iterations",
                "2",
                "--timeout",
                "120",
                "--max-memory",
                "1024",
                "--warmup-runs",
                "1",
                "--cooldown",
                "3",
                "--enable-quality-assessment",
                "--save-extracted-text",
            ],
        )

        assert result.exit_code == 0
        mock_engine.assert_called_once()


def test_command_help_messages() -> None:
    """Test that all commands have proper help messages."""
    commands = ["benchmark", "report", "visualize", "aggregate", "list-frameworks", "list-categories"]
    runner = CliRunner()

    for command in commands:
        result = runner.invoke(main, [command, "--help"])
        assert result.exit_code == 0
        assert len(result.output) > 50
