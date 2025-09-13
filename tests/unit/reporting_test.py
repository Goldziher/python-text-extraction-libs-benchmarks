"""Tests for reporting module using real benchmark data."""

import tempfile
from pathlib import Path

import pytest

from src.types import (
    BenchmarkResult,
    BenchmarkSummary,
    DocumentCategory,
    ExtractionStatus,
    FileType,
    Framework,
)


class TestReportingModule:
    """Test the reporting functionality with realistic data."""

    def setup_method(self):
        """Set up test data."""
        # Create realistic benchmark results
        self.sample_results = [
            BenchmarkResult(
                file_path="test_documents/pdfs/sample.pdf",
                file_size=1024000,  # 1MB
                file_type=FileType.PDF,
                category=DocumentCategory.SMALL,
                framework=Framework.KREUZBERG_SYNC,
                iteration=1,
                extraction_time=2.5,
                peak_memory_mb=150.0,
                avg_memory_mb=120.0,
                peak_cpu_percent=85.0,
                avg_cpu_percent=65.0,
                status=ExtractionStatus.SUCCESS,
                character_count=5000,
                word_count=800,
                attempts=1,
            ),
            BenchmarkResult(
                file_path="test_documents/office/document.docx",
                file_size=512000,  # 512KB
                file_type=FileType.DOCX,
                category=DocumentCategory.SMALL,
                framework=Framework.KREUZBERG_SYNC,
                iteration=1,
                extraction_time=1.8,
                peak_memory_mb=140.0,
                avg_memory_mb=110.0,
                peak_cpu_percent=75.0,
                avg_cpu_percent=55.0,
                status=ExtractionStatus.SUCCESS,
                character_count=3500,
                word_count=600,
                attempts=1,
            ),
            BenchmarkResult(
                file_path="test_documents/large/big_document.pdf",
                file_size=5120000,  # 5MB
                file_type=FileType.PDF,
                category=DocumentCategory.MEDIUM,
                framework=Framework.KREUZBERG_SYNC,
                iteration=1,
                extraction_time=0.0,  # Timeout case
                peak_memory_mb=0.0,
                avg_memory_mb=0.0,
                peak_cpu_percent=0.0,
                avg_cpu_percent=0.0,
                status=ExtractionStatus.TIMEOUT,
                error_type="TimeoutError",
                error_message="Extraction timed out after 300 seconds",
                attempts=3,
            ),
            BenchmarkResult(
                file_path="test_documents/images/chart.png",
                file_size=256000,  # 256KB
                file_type=FileType.IMAGE_PNG,
                category=DocumentCategory.TINY,
                framework=Framework.KREUZBERG_ASYNC,
                iteration=1,
                extraction_time=3.2,
                peak_memory_mb=180.0,
                avg_memory_mb=150.0,
                peak_cpu_percent=90.0,
                avg_cpu_percent=70.0,
                status=ExtractionStatus.SUCCESS,
                character_count=200,
                word_count=45,
                attempts=1,
            ),
            BenchmarkResult(
                file_path="test_documents/corrupted/bad_file.pdf",
                file_size=1024,
                file_type=FileType.PDF,
                category=DocumentCategory.TINY,
                framework=Framework.DOCLING,
                iteration=1,
                extraction_time=0.5,
                peak_memory_mb=50.0,
                avg_memory_mb=40.0,
                peak_cpu_percent=30.0,
                avg_cpu_percent=25.0,
                status=ExtractionStatus.FAILED,
                error_type="ValueError",
                error_message="Unsupported file format",
                attempts=2,
            ),
        ]

        # Create realistic benchmark summaries
        self.sample_summaries = [
            BenchmarkSummary(
                framework=Framework.KREUZBERG_SYNC,
                category=DocumentCategory.SMALL,
                total_files=2,
                successful_files=2,
                failed_files=0,
                partial_files=0,
                timeout_files=0,
                avg_extraction_time=2.15,
                median_extraction_time=2.15,
                min_extraction_time=1.8,
                max_extraction_time=2.5,
                std_extraction_time=0.35,
                avg_peak_memory_mb=145.0,
                avg_cpu_percent=60.0,
                files_per_second=0.47,
                mb_per_second=0.36,
                success_rate=1.0,
                avg_character_count=4250,
                avg_word_count=700,
            ),
            BenchmarkSummary(
                framework=Framework.KREUZBERG_ASYNC,
                category=DocumentCategory.TINY,
                total_files=1,
                successful_files=1,
                failed_files=0,
                partial_files=0,
                timeout_files=0,
                avg_extraction_time=3.2,
                median_extraction_time=3.2,
                min_extraction_time=3.2,
                max_extraction_time=3.2,
                std_extraction_time=0.0,
                avg_peak_memory_mb=180.0,
                avg_cpu_percent=70.0,
                files_per_second=0.31,
                mb_per_second=0.08,
                success_rate=1.0,
                avg_character_count=200,
                avg_word_count=45,
            ),
            BenchmarkSummary(
                framework=Framework.DOCLING,
                category=DocumentCategory.TINY,
                total_files=1,
                successful_files=0,
                failed_files=1,
                partial_files=0,
                timeout_files=0,
                avg_extraction_time=0.5,
                median_extraction_time=0.5,
                min_extraction_time=0.5,
                max_extraction_time=0.5,
                std_extraction_time=0.0,
                avg_peak_memory_mb=50.0,
                avg_cpu_percent=25.0,
                files_per_second=2.0,
                mb_per_second=0.002,
                success_rate=0.0,
                avg_character_count=0,
                avg_word_count=0,
            ),
        ]

    def test_console_report_generation(self):
        """Test console report generation with sample data."""
        report = generate_console_report(self.sample_results)

        assert isinstance(report, str)
        assert len(report) > 0

        # Check that report contains key information
        assert "Framework" in report
        assert "Success Rate" in report
        assert "kreuzberg_sync" in report
        assert "kreuzberg_async" in report
        assert "docling" in report

        # Check that it includes performance metrics
        assert "files/sec" in report or "Files/Sec" in report
        assert "Memory" in report or "memory" in report

    def test_console_report_with_empty_results(self):
        """Test console report generation with empty results."""
        empty_results = []

        report = generate_console_report(empty_results)

        assert isinstance(report, str)
        # Should handle empty results gracefully
        assert "No results" in report or len(report.strip()) == 0

    def test_console_report_success_rate_calculation(self):
        """Test that success rates are calculated correctly in reports."""
        report = generate_console_report(self.sample_results)

        # Should show different success rates for different frameworks
        # Kreuzberg should have high success rate (2/2 for sync, 1/1 for async)
        # Docling should have 0% success rate (0/1)

        assert "100" in report or "1.0" in report  # High success rate
        assert "0" in report or "0.0" in report  # Zero success rate

    def test_html_report_generation(self):
        """Test HTML report generation with sample data."""
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".html", delete=False) as f:
            output_file = Path(f.name)

        try:
            generate_html_report(self.sample_results, output_file)

            assert output_file.exists()

            # Read and verify HTML content
            html_content = output_file.read_text()

            assert "<html" in html_content
            assert "<table" in html_content
            assert "kreuzberg_sync" in html_content
            assert "SUCCESS" in html_content or "FAILED" in html_content

            # Check for CSS styling
            assert "style" in html_content or ".css" in html_content

        finally:
            output_file.unlink()

    def test_html_report_with_timeout_results(self):
        """Test HTML report handles timeout results correctly."""
        timeout_results = [result for result in self.sample_results if result.status == ExtractionStatus.TIMEOUT]

        if not timeout_results:
            # Add a timeout result for testing
            timeout_result = BenchmarkResult(
                file_path="test_timeout.pdf",
                file_size=1000000,
                file_type=FileType.PDF,
                category=DocumentCategory.MEDIUM,
                framework=Framework.KREUZBERG_SYNC,
                iteration=1,
                extraction_time=300.0,  # Full timeout duration
                peak_memory_mb=0.0,
                avg_memory_mb=0.0,
                peak_cpu_percent=0.0,
                avg_cpu_percent=0.0,
                status=ExtractionStatus.TIMEOUT,
                error_type="TimeoutError",
                error_message="Extraction timed out after 300 seconds",
                attempts=3,
            )
            timeout_results = [timeout_result]

        with tempfile.NamedTemporaryFile(mode="w+", suffix=".html", delete=False) as f:
            output_file = Path(f.name)

        try:
            generate_html_report(timeout_results, output_file)

            assert output_file.exists()

            html_content = output_file.read_text()
            assert "TIMEOUT" in html_content
            assert "timeout" in html_content.lower()

        finally:
            output_file.unlink()

    def test_report_framework_comparison(self):
        """Test that reports properly compare different frameworks."""
        report = generate_console_report(self.sample_results)

        # Should include all frameworks present in sample data
        frameworks_in_data = {result.framework.value for result in self.sample_results}

        for framework in frameworks_in_data:
            assert framework in report

        # Should show comparative metrics
        assert any(metric in report for metric in ["faster", "slower", "better", "worse"]) or any(
            number in report for number in ["1.", "2.", "3."]
        )  # Rankings

    def test_report_category_breakdown(self):
        """Test that reports include category-based breakdown."""
        report = generate_console_report(self.sample_results)

        # Should include category information
        categories_in_data = {result.category.value for result in self.sample_results}

        for category in categories_in_data:
            assert category in report

    def test_report_error_analysis(self):
        """Test that reports include error analysis for failed extractions."""
        failed_results = [result for result in self.sample_results if result.status == ExtractionStatus.FAILED]

        if not failed_results:
            pytest.skip("No failed results in sample data")

        report = generate_console_report(self.sample_results)

        # Should include error information
        assert "error" in report.lower() or "failed" in report.lower()
        assert "ValueError" in report  # Specific error from sample data

    def test_report_performance_metrics(self):
        """Test that reports include comprehensive performance metrics."""
        report = generate_console_report(self.sample_results)

        # Should include timing metrics
        timing_keywords = ["time", "second", "ms", "duration"]
        assert any(keyword in report.lower() for keyword in timing_keywords)

        # Should include memory metrics
        memory_keywords = ["memory", "mb", "ram"]
        assert any(keyword in report.lower() for keyword in memory_keywords)

        # Should include CPU metrics
        cpu_keywords = ["cpu", "processor", "percent", "%"]
        assert any(keyword in report.lower() for keyword in cpu_keywords)

        # Should include throughput metrics
        throughput_keywords = ["files/sec", "mb/sec", "throughput", "rate"]
        assert any(keyword in report.lower() for keyword in throughput_keywords)

    def test_report_data_integrity(self):
        """Test that reports maintain data integrity from source results."""
        report = generate_console_report(self.sample_results)

        # Check that specific values from sample data appear in report
        # (allowing for rounding/formatting differences)

        # Should include file counts
        total_files = len(self.sample_results)
        assert str(total_files) in report

        # Should include success/failure information
        success_count = len([r for r in self.sample_results if r.status == ExtractionStatus.SUCCESS])
        assert str(success_count) in report or f"{success_count}" in report

    def test_report_formatting_consistency(self):
        """Test that report formatting is consistent and readable."""
        report = generate_console_report(self.sample_results)

        # Should have consistent formatting
        lines = report.split("\n")

        # Should have headers/sections
        assert len(lines) > 5  # Multiple lines of content

        # Should not have excessive blank lines
        blank_lines = [line for line in lines if line.strip() == ""]
        assert len(blank_lines) < len(lines) / 2  # Less than 50% blank lines

    def test_summary_report_generation(self):
        """Test generation of summary reports from BenchmarkSummary objects."""
        from src.reporting import generate_summary_report

        summary_report = generate_summary_report(self.sample_summaries)

        assert isinstance(summary_report, str)
        assert len(summary_report) > 0

        # Should include framework names
        for summary in self.sample_summaries:
            assert summary.framework.value in summary_report

        # Should include key metrics
        assert any(metric in summary_report.lower() for metric in ["success rate", "files/sec", "memory"])

    def test_report_with_quality_metrics(self):
        """Test reporting when quality metrics are available."""
        # Add quality metrics to sample results
        enhanced_results = []

        for result in self.sample_results:
            if result.status == ExtractionStatus.SUCCESS:
                # Add quality metrics
                enhanced_result = BenchmarkResult(
                    **result.__dict__,
                    avg_quality_score=0.85,
                    min_quality_score=0.75,
                    max_quality_score=0.95,
                    avg_completeness=0.90,
                    avg_coherence=0.80,
                    avg_readability=0.75,
                )
                enhanced_results.append(enhanced_result)
            else:
                enhanced_results.append(result)

        if not enhanced_results:
            pytest.skip("No enhanced results to test")

        report = generate_console_report(enhanced_results)

        # Should include quality information
        quality_keywords = ["quality", "completeness", "coherence", "readability"]
        assert any(keyword in report.lower() for keyword in quality_keywords)

    def test_report_statistical_accuracy(self):
        """Test that statistical calculations in reports are accurate."""
        # Focus on results from one framework for clear statistics
        kreuzberg_results = [
            r
            for r in self.sample_results
            if r.framework == Framework.KREUZBERG_SYNC and r.status == ExtractionStatus.SUCCESS
        ]

        if len(kreuzberg_results) < 2:
            pytest.skip("Need multiple successful results for statistical testing")

        report = generate_console_report(kreuzberg_results)

        # Calculate expected statistics
        extraction_times = [r.extraction_time for r in kreuzberg_results]
        expected_avg = sum(extraction_times) / len(extraction_times)

        # Check if average appears in report (allowing for rounding)
        avg_str = f"{expected_avg:.1f}"
        assert avg_str in report or f"{expected_avg:.2f}" in report

    def test_multilingual_content_handling(self):
        """Test report generation with multilingual file paths and content."""
        # Create results with multilingual file paths
        multilingual_results = [
            BenchmarkResult(
                file_path="test_documents/עברית/מסמך_עברי.pdf",  # Hebrew
                file_size=1024000,
                file_type=FileType.PDF,
                category=DocumentCategory.SMALL,
                framework=Framework.KREUZBERG_SYNC,
                iteration=1,
                extraction_time=2.5,
                peak_memory_mb=150.0,
                avg_memory_mb=120.0,
                peak_cpu_percent=85.0,
                avg_cpu_percent=65.0,
                status=ExtractionStatus.SUCCESS,
                character_count=5000,
                word_count=800,
                attempts=1,
            ),
            BenchmarkResult(
                file_path="test_documents/中文/中文文档.pdf",  # Chinese
                file_size=2048000,
                file_type=FileType.PDF,
                category=DocumentCategory.SMALL,
                framework=Framework.KREUZBERG_SYNC,
                iteration=1,
                extraction_time=3.0,
                peak_memory_mb=160.0,
                avg_memory_mb=130.0,
                peak_cpu_percent=80.0,
                avg_cpu_percent=60.0,
                status=ExtractionStatus.SUCCESS,
                character_count=6000,
                word_count=400,  # Chinese has different word count characteristics
                attempts=1,
            ),
        ]

        # Should handle multilingual paths without errors
        try:
            report = generate_console_report(multilingual_results)
            assert isinstance(report, str)
            assert len(report) > 0
        except UnicodeError:
            pytest.fail("Report generation failed with multilingual content")

        # HTML report should also handle multilingual content
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".html", delete=False, encoding="utf-8") as f:
            output_file = Path(f.name)

        try:
            generate_html_report(multilingual_results, output_file)
            assert output_file.exists()

            # Should contain UTF-8 charset declaration
            html_content = output_file.read_text(encoding="utf-8")
            assert "charset" in html_content.lower() or "utf-8" in html_content.lower()

        finally:
            output_file.unlink()
