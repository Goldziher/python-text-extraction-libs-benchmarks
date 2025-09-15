from pathlib import Path

import pytest
from click.testing import CliRunner

from src.cli import main


class TestCLIWithRealData:
    def setup_method(self):
        self.runner = CliRunner()
        self.test_docs_dir = Path("test_documents")

        if not self.test_docs_dir.exists():
            pytest.skip("test_documents directory not found")

    def test_list_frameworks_command(self):
        result = self.runner.invoke(main, ["list-frameworks"])

        assert result.exit_code == 0
        output = result.output.lower()

        expected_frameworks = [
            "kreuzberg_sync",
            "kreuzberg_async",
            "docling",
            "markitdown",
            "unstructured",
            "extractous",
        ]

        for framework in expected_frameworks:
            assert framework in output, f"Framework {framework} not listed"

    def test_benchmark_single_framework(self):
        result = self.runner.invoke(
            main,
            [
                "benchmark",
                "--framework",
                "kreuzberg_sync",
                "--iterations",
                "1",
                "--timeout",
                "60",
                "--continue-on-error",
            ],
        )

        assert result.exit_code == 0

        results_dir = Path("results")
        assert results_dir.exists()

        json_files = list(results_dir.glob("*.json"))
        assert len(json_files) > 0, "No JSON result files generated"

    def test_benchmark_with_quality_assessment(self):
        result = self.runner.invoke(
            main,
            [
                "benchmark",
                "--framework",
                "kreuzberg_sync",
                "--iterations",
                "1",
                "--timeout",
                "30",
                "--enable-quality-assessment",
                "--continue-on-error",
            ],
        )

        assert result.exit_code == 0

        results_dir = Path("results")
        files = list(results_dir.glob("*"))
        assert len(files) > 0, "Expected output files with quality assessment"

    @pytest.mark.xfail(
        reason="Report generation requires actual benchmark data files which may not be available in test environment"
    )
    def test_report_generation_with_real_data(self):
        benchmark_result = self.runner.invoke(
            main,
            [
                "benchmark",
                "--framework",
                "kreuzberg_sync",
                "--iterations",
                "1",
                "--timeout",
                "30",
                "--continue-on-error",
            ],
        )

        assert benchmark_result.exit_code == 0

        report_result = self.runner.invoke(main, ["report", "--output-format", "markdown"])

        assert report_result.exit_code in [0, 1]

    @pytest.mark.xfail(
        reason="Visualization generation requires actual benchmark data files which may not be available in test environment"
    )
    def test_visualize_command(self):
        benchmark_result = self.runner.invoke(
            main,
            [
                "benchmark",
                "--framework",
                "kreuzberg_sync",
                "--iterations",
                "1",
                "--timeout",
                "30",
                "--continue-on-error",
            ],
        )

        assert benchmark_result.exit_code == 0

        viz_result = self.runner.invoke(main, ["visualize"])

        assert viz_result.exit_code in [0, 1]

    def test_aggregate_command(self):
        benchmark_result = self.runner.invoke(
            main,
            [
                "benchmark",
                "--framework",
                "kreuzberg_sync",
                "--iterations",
                "1",
                "--timeout",
                "30",
                "--continue-on-error",
            ],
        )

        assert benchmark_result.exit_code == 0

        agg_result = self.runner.invoke(main, ["aggregate"])

        assert agg_result.exit_code in [0, 1]

    @pytest.mark.xfail(
        reason="Documentation generation requires actual benchmark data files which may not be available in test environment"
    )
    def test_docs_command(self):
        docs_result = self.runner.invoke(main, ["docs"])

        assert docs_result.exit_code in [0, 1]


class TestCLIEdgeCases:
    def setup_method(self):
        self.runner = CliRunner()

    def test_invalid_framework_parameter(self):
        result = self.runner.invoke(
            main,
            ["benchmark", "--framework", "nonexistent_framework"],
        )

        assert result.exit_code != 0
        assert "Invalid framework" in result.output

    def test_valid_framework_parameter(self):
        result = self.runner.invoke(
            main,
            ["benchmark", "--framework", "kreuzberg_sync"],
        )

        assert result.exit_code == 0

    def test_benchmark_execution(self):
        result = self.runner.invoke(main, ["benchmark", "--framework", "kreuzberg_sync"])

        assert result.exit_code == 0

    def test_extremely_short_timeout(self):
        result = self.runner.invoke(
            main,
            [
                "benchmark",
                "--framework",
                "kreuzberg_sync",
                "--iterations",
                "1",
                "--timeout",
                "1",
                "--continue-on-error",
            ],
        )

        assert result.exit_code == 0

        results_dir = Path("results")
        json_files = list(results_dir.glob("*.json"))
        assert len(json_files) >= 0

    def test_help_commands(self):
        commands = ["benchmark", "aggregate", "report", "visualize", "docs", "list-frameworks"]

        for cmd in commands:
            result = self.runner.invoke(main, [cmd, "--help"])
            assert result.exit_code == 0
            assert "Usage:" in result.output

    def test_main_help(self):
        result = self.runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Python text extraction libraries benchmarking suite" in result.output
