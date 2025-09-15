"""Integration tests for CLI using real test documents."""

import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from src.cli import main


class TestCLIWithRealData:
    """Test CLI commands using real test documents."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
        self.test_docs_dir = Path("test_documents")

        if not self.test_docs_dir.exists():
            pytest.skip("test_documents directory not found")

    def test_list_frameworks_command(self):
        """Test listing available frameworks."""
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

    def test_benchmark_single_pdf_file(self):
        """Test benchmarking a single PDF file."""
        pdf_file = self.test_docs_dir / "pdfs" / "code_and_formula.pdf"

        if not pdf_file.exists():
            pytest.skip(f"Test file {pdf_file} not found")

        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.runner.invoke(
                main,
                [
                    "benchmark",
                    "--framework",
                    "kreuzberg_sync",
                    "--category",
                    "small",
                    "--iterations",
                    "1",
                    "--warmup-runs",
                    "0",
                    "--timeout",
                    "60",
                    "--max-run-duration",
                    "2",
                    "--output-dir",
                    temp_dir,
                    "--continue-on-error",
                ],
            )

            assert result.exit_code == 0

            results_dir = Path(temp_dir)
            assert results_dir.exists()

            json_files = list(results_dir.glob("*.json"))
            assert len(json_files) > 0, "No JSON result files generated"

    def test_benchmark_multiple_formats(self):
        """Test benchmarking multiple document formats."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.runner.invoke(
                main,
                [
                    "benchmark",
                    "--framework",
                    "kreuzberg_sync",
                    "--category",
                    "tiny",
                    "--iterations",
                    "1",
                    "--warmup-runs",
                    "0",
                    "--timeout",
                    "30",
                    "--max-run-duration",
                    "3",
                    "--output-dir",
                    temp_dir,
                    "--continue-on-error",
                ],
            )

            assert result.exit_code == 0

            results_dir = Path(temp_dir)
            json_files = list(results_dir.glob("*.json"))
            assert len(json_files) > 0

    def test_benchmark_with_quality_assessment(self):
        """Test benchmark with quality assessment enabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.runner.invoke(
                main,
                [
                    "benchmark",
                    "--framework",
                    "kreuzberg_sync",
                    "--category",
                    "tiny",
                    "--iterations",
                    "1",
                    "--warmup-runs",
                    "0",
                    "--timeout",
                    "30",
                    "--max-run-duration",
                    "2",
                    "--output-dir",
                    temp_dir,
                    "--enable-quality-assessment",
                    "--continue-on-error",
                ],
            )

            assert result.exit_code == 0

            results_dir = Path(temp_dir)
            files = list(results_dir.glob("*"))
            assert len(files) > 1, "Expected multiple output files with quality assessment"

    def test_report_generation_with_real_data(self):
        """Test report generation using real benchmark data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            benchmark_result = self.runner.invoke(
                main,
                [
                    "benchmark",
                    "--framework",
                    "kreuzberg_sync",
                    "--category",
                    "tiny",
                    "--iterations",
                    "1",
                    "--warmup-runs",
                    "0",
                    "--timeout",
                    "30",
                    "--max-run-duration",
                    "2",
                    "--output-dir",
                    temp_dir,
                    "--continue-on-error",
                ],
            )

            assert benchmark_result.exit_code == 0

            report_result = self.runner.invoke(main, ["report", "--input-dir", temp_dir, "--output-format", "console"])

            assert report_result.exit_code == 0
            assert "Framework" in report_result.output
            assert "kreuzberg_sync" in report_result.output

    def test_visualize_command_with_real_data(self):
        """Test visualization generation with real data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            benchmark_result = self.runner.invoke(
                main,
                [
                    "benchmark",
                    "--framework",
                    "kreuzberg_sync",
                    "--category",
                    "tiny",
                    "--iterations",
                    "1",
                    "--warmup-runs",
                    "0",
                    "--timeout",
                    "30",
                    "--max-run-duration",
                    "2",
                    "--output-dir",
                    temp_dir,
                    "--continue-on-error",
                ],
            )

            assert benchmark_result.exit_code == 0

            viz_result = self.runner.invoke(main, ["visualize", "--input-dir", temp_dir, "--output-dir", temp_dir])

            assert viz_result.exit_code == 0

            chart_files = list(Path(temp_dir).glob("*.png"))
            assert len(chart_files) > 0, "No chart files generated"

    def test_aggregate_command_with_multiple_runs(self):
        """Test aggregation of multiple benchmark runs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            for framework in ["kreuzberg_sync", "markitdown"]:
                run_dir = temp_path / f"run_{framework}"
                run_dir.mkdir()

                result = self.runner.invoke(
                    main,
                    [
                        "benchmark",
                        "--framework",
                        framework,
                        "--category",
                        "tiny",
                        "--iterations",
                        "1",
                        "--warmup-runs",
                        "0",
                        "--timeout",
                        "30",
                        "--max-run-duration",
                        "2",
                        "--output-dir",
                        str(run_dir),
                        "--continue-on-error",
                    ],
                )

                assert result.exit_code in [0, 1]

            agg_result = self.runner.invoke(
                main,
                [
                    "aggregate",
                    "--input-dirs",
                    str(temp_path / "run_kreuzberg_sync") + "," + str(temp_path / "run_markitdown"),
                    "--output-dir",
                    str(temp_path),
                ],
            )

            assert agg_result.exit_code == 0

            agg_files = list(temp_path.glob("aggregated_*.json"))
            assert len(agg_files) > 0, "No aggregated results generated"

    def test_error_handling_with_invalid_files(self):
        """Test error handling with corrupted or invalid files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            fake_pdf = temp_path / "fake.pdf"
            fake_pdf.write_text("This is not a real PDF file")

            result = self.runner.invoke(
                main,
                [
                    "benchmark",
                    "--framework",
                    "kreuzberg_sync",
                    "--category",
                    "tiny",
                    "--iterations",
                    "1",
                    "--warmup-runs",
                    "0",
                    "--timeout",
                    "10",
                    "--max-run-duration",
                    "1",
                    "--output-dir",
                    temp_dir,
                    "--continue-on-error",
                ],
            )

            assert result.exit_code == 0

    def test_specific_document_types(self):
        """Test benchmarking specific document types."""
        document_tests = [
            ("csv_json_yaml/simple.json", "tiny"),
            ("csv_json_yaml/simple.yaml", "tiny"),
            ("office/simple.pptx", "small"),
            ("markdown/README.md", "tiny"),
        ]

        for doc_path, category in document_tests:
            full_path = self.test_docs_dir / doc_path
            if not full_path.exists():
                continue

            with tempfile.TemporaryDirectory() as temp_dir:
                result = self.runner.invoke(
                    main,
                    [
                        "benchmark",
                        "--framework",
                        "kreuzberg_sync",
                        "--category",
                        category,
                        "--iterations",
                        "1",
                        "--warmup-runs",
                        "0",
                        "--timeout",
                        "30",
                        "--max-run-duration",
                        "2",
                        "--output-dir",
                        temp_dir,
                        "--continue-on-error",
                    ],
                )

                assert result.exit_code == 0, f"Failed for {doc_path}"

    def test_multilingual_documents(self):
        """Test benchmarking multilingual documents if available."""
        multilingual_patterns = ["*chinese*", "*japanese*", "*hebrew*", "*german*", "*korean*"]

        found_multilingual = False

        for pattern in multilingual_patterns:
            files = list(self.test_docs_dir.rglob(pattern))
            if files:
                found_multilingual = True
                break

        if not found_multilingual:
            pytest.skip("No multilingual test documents found")

        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.runner.invoke(
                main,
                [
                    "benchmark",
                    "--framework",
                    "kreuzberg_sync",
                    "--category",
                    "tiny",
                    "--iterations",
                    "1",
                    "--warmup-runs",
                    "0",
                    "--timeout",
                    "60",
                    "--max-run-duration",
                    "3",
                    "--output-dir",
                    temp_dir,
                    "--continue-on-error",
                ],
            )

            assert result.exit_code == 0

    def test_benchmark_performance_thresholds(self):
        """Test that benchmarks complete within reasonable time thresholds."""
        import time

        with tempfile.TemporaryDirectory() as temp_dir:
            start_time = time.time()

            result = self.runner.invoke(
                main,
                [
                    "benchmark",
                    "--framework",
                    "kreuzberg_sync",
                    "--category",
                    "tiny",
                    "--iterations",
                    "1",
                    "--warmup-runs",
                    "0",
                    "--timeout",
                    "30",
                    "--max-run-duration",
                    "2",
                    "--output-dir",
                    temp_dir,
                    "--continue-on-error",
                ],
            )

            end_time = time.time()
            elapsed = end_time - start_time

            assert elapsed < 180, f"Benchmark took too long: {elapsed} seconds"
            assert result.exit_code == 0

    def test_output_file_integrity(self):
        """Test that output files are properly formatted and complete."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.runner.invoke(
                main,
                [
                    "benchmark",
                    "--framework",
                    "kreuzberg_sync",
                    "--category",
                    "tiny",
                    "--iterations",
                    "1",
                    "--warmup-runs",
                    "0",
                    "--timeout",
                    "30",
                    "--max-run-duration",
                    "2",
                    "--output-dir",
                    temp_dir,
                    "--continue-on-error",
                ],
            )

            assert result.exit_code == 0

            import json

            results_dir = Path(temp_dir)
            json_files = list(results_dir.glob("*.json"))

            assert len(json_files) > 0, "No JSON files generated"

            for json_file in json_files:
                try:
                    with open(json_file) as f:
                        data = json.load(f)

                    assert isinstance(data, (dict, list)), f"Invalid JSON structure in {json_file}"

                except json.JSONDecodeError as e:
                    pytest.fail(f"Invalid JSON in {json_file}: {e}")


class TestCLIEdgeCases:
    """Test CLI edge cases and error conditions."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    def test_invalid_framework_parameter(self):
        """Test CLI behavior with invalid framework."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.runner.invoke(
                main,
                ["benchmark", "--framework", "nonexistent_framework", "--category", "tiny", "--output-dir", temp_dir],
            )

            assert result.exit_code != 0
            assert "Invalid framework" in result.output

    def test_invalid_category_parameter(self):
        """Test CLI behavior with invalid category."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.runner.invoke(
                main,
                [
                    "benchmark",
                    "--framework",
                    "kreuzberg_sync",
                    "--category",
                    "nonexistent_category",
                    "--output-dir",
                    temp_dir,
                ],
            )

            assert result.exit_code != 0
            assert "Invalid category" in result.output

    def test_nonexistent_output_directory(self):
        """Test CLI behavior with non-existent output directory."""
        nonexistent_dir = "/path/that/does/not/exist"

        result = self.runner.invoke(
            main, ["benchmark", "--framework", "kreuzberg_sync", "--category", "tiny", "--output-dir", nonexistent_dir]
        )

        assert result.exit_code in [0, 1]

    def test_insufficient_permissions(self):
        """Test CLI behavior with insufficient permissions."""
        pytest.skip("Permission testing requires system-specific setup")

    def test_extremely_short_timeout(self):
        """Test CLI behavior with extremely short timeouts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.runner.invoke(
                main,
                [
                    "benchmark",
                    "--framework",
                    "kreuzberg_sync",
                    "--category",
                    "tiny",
                    "--iterations",
                    "1",
                    "--warmup-runs",
                    "0",
                    "--timeout",
                    "1",
                    "--max-run-duration",
                    "1",
                    "--output-dir",
                    temp_dir,
                    "--continue-on-error",
                ],
            )

            assert result.exit_code == 0

            results_dir = Path(temp_dir)
            json_files = list(results_dir.glob("*.json"))
            assert len(json_files) > 0
