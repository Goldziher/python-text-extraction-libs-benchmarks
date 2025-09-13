"""Integration tests for timeout handling across the system."""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.benchmark import ComprehensiveBenchmarkRunner
from src.types import (
    BenchmarkConfig,
    DocumentCategory,
    ExtractionStatus,
    Framework,
)


class TestTimeoutIntegration:
    """Test timeout handling across the entire system."""

    @pytest.mark.asyncio
    async def test_benchmark_suite_timeout_short_duration(self):
        """Test that benchmark suite respects max_run_duration timeout."""
        config = BenchmarkConfig(
            frameworks=[Framework.KREUZBERG_SYNC],
            categories=[DocumentCategory.TINY],
            iterations=1,
            warmup_runs=0,
            max_run_duration_minutes=0.02,  # 1.2 seconds - very short
            output_dir=Path("test_output"),
        )

        runner = ComprehensiveBenchmarkRunner(config)

        # Mock file discovery to return a test file
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"Test content")
            test_file = Path(f.name)

        try:
            # Mock the categorizer to return our test file
            with (
                patch.object(runner.categorizer, "get_files_by_category") as mock_get_files,
                patch("src.benchmark.get_extractor") as mock_get_extractor,
            ):
                mock_get_files.return_value = [test_file]

                # Mock extractor that takes too long
                mock_extractor = Mock()
                mock_extractor.extract_text.side_effect = lambda x: asyncio.sleep(10)  # 10 second delay
                mock_get_extractor.return_value = mock_extractor

                start_time = asyncio.get_event_loop().time()
                results = await runner.run_benchmark_suite()
                end_time = asyncio.get_event_loop().time()

                # Should complete within timeout window (plus small buffer)
                elapsed_seconds = end_time - start_time
                assert elapsed_seconds < 5  # Should timeout way before 10 seconds

                # Results should be empty or contain timeout markers
                assert isinstance(results, list)

        finally:
            test_file.unlink()

    @pytest.mark.asyncio
    async def test_individual_file_timeout(self):
        """Test timeout handling for individual file extraction."""
        config = BenchmarkConfig(
            frameworks=[Framework.KREUZBERG_SYNC],
            categories=[DocumentCategory.TINY],
            iterations=1,
            warmup_runs=0,
            timeout_seconds=1,  # Very short timeout for individual files
            output_dir=Path("test_output"),
        )

        runner = ComprehensiveBenchmarkRunner(config)

        # Create test file
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"Test content for timeout testing")
            test_file = Path(f.name)

        try:
            with patch("src.benchmark.get_extractor") as mock_get_extractor:
                # Mock slow extractor
                mock_extractor = Mock()

                # Create an async function that sleeps longer than timeout
                async def slow_extract(file_path):
                    await asyncio.sleep(5)  # 5 seconds - longer than 1 second timeout
                    return "extracted text"

                mock_extractor.extract_text = slow_extract
                mock_get_extractor.return_value = mock_extractor

                # Mock file metadata
                mock_metadata = {
                    "file_size": 1000,
                    "file_type": "txt",
                }

                with patch.object(runner.categorizer, "_get_file_metadata") as mock_metadata_func:
                    mock_metadata_func.return_value = mock_metadata

                    # This should timeout at the file level
                    result = await runner._benchmark_single_file(
                        Framework.KREUZBERG_SYNC, test_file, mock_metadata, 0, DocumentCategory.TINY
                    )

                    # Should return a timeout result
                    assert result is not None
                    assert result.status == ExtractionStatus.TIMEOUT
                    assert "timeout" in result.error_message.lower()

        finally:
            test_file.unlink()

    @pytest.mark.asyncio
    async def test_timeout_recovery_and_partial_results(self):
        """Test that timeout allows recovery and saves partial results."""
        config = BenchmarkConfig(
            frameworks=[Framework.KREUZBERG_SYNC],
            categories=[DocumentCategory.TINY],
            iterations=2,
            warmup_runs=0,
            max_run_duration_minutes=0.05,  # 3 seconds
            output_dir=Path("test_output"),
        )

        runner = ComprehensiveBenchmarkRunner(config)

        # Create test files
        test_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(suffix=f"_test{i}.txt", delete=False) as f:
                f.write(f"Test content {i}".encode())
                test_files.append(Path(f.name))

        try:
            with (
                patch.object(runner.categorizer, "get_files_by_category") as mock_get_files,
                patch("src.benchmark.get_extractor") as mock_get_extractor,
                patch.object(runner, "_save_results") as mock_save,
            ):
                mock_get_files.return_value = test_files

                # Mock extractor - first file fast, others slow
                mock_extractor = Mock()

                call_count = 0

                async def variable_speed_extract(file_path):
                    nonlocal call_count
                    call_count += 1
                    if call_count == 1:
                        await asyncio.sleep(0.1)  # Fast
                        return "extracted text 1"
                    await asyncio.sleep(10)  # Very slow - will timeout
                    return "extracted text slow"

                mock_extractor.extract_text = variable_speed_extract
                mock_get_extractor.return_value = mock_extractor

                results = await runner.run_benchmark_suite()

                # Should have some results before timeout
                # At minimum, should have called save_results to preserve partial results
                mock_save.assert_called()

        finally:
            for test_file in test_files:
                test_file.unlink()

    @pytest.mark.asyncio
    async def test_async_extractor_timeout_handling(self):
        """Test timeout handling specifically for async extractors."""
        config = BenchmarkConfig(
            frameworks=[Framework.KREUZBERG_ASYNC],
            categories=[DocumentCategory.TINY],
            iterations=1,
            warmup_runs=0,
            timeout_seconds=1,
            output_dir=Path("test_output"),
        )

        runner = ComprehensiveBenchmarkRunner(config)

        # Create test file
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"Test async timeout")
            test_file = Path(f.name)

        try:
            with patch("src.benchmark.get_extractor") as mock_get_extractor:
                # Mock async extractor
                mock_extractor = AsyncMock()
                mock_extractor.extract_text.side_effect = lambda x: asyncio.sleep(5)
                mock_get_extractor.return_value = mock_extractor

                mock_metadata = {"file_size": 1000, "file_type": "txt"}

                with patch.object(runner.categorizer, "_get_file_metadata") as mock_metadata_func:
                    mock_metadata_func.return_value = mock_metadata

                    result = await runner._benchmark_single_file(
                        Framework.KREUZBERG_ASYNC, test_file, mock_metadata, 0, DocumentCategory.TINY
                    )

                    assert result is not None
                    assert result.status == ExtractionStatus.TIMEOUT

        finally:
            test_file.unlink()

    @pytest.mark.asyncio
    async def test_concurrent_timeout_handling(self):
        """Test timeout handling when multiple files are processed concurrently."""
        config = BenchmarkConfig(
            frameworks=[Framework.KREUZBERG_SYNC],
            categories=[DocumentCategory.TINY],
            iterations=1,
            warmup_runs=0,
            timeout_seconds=2,
            concurrent_files=2,  # Process 2 files at once
            output_dir=Path("test_output"),
        )

        runner = ComprehensiveBenchmarkRunner(config)

        # Create multiple test files
        test_files = []
        for i in range(4):
            with tempfile.NamedTemporaryFile(suffix=f"_concurrent{i}.txt", delete=False) as f:
                f.write(f"Concurrent test content {i}".encode())
                test_files.append(Path(f.name))

        try:
            with (
                patch.object(runner.categorizer, "get_files_by_category") as mock_get_files,
                patch("src.benchmark.get_extractor") as mock_get_extractor,
            ):
                mock_get_files.return_value = test_files

                # Mock extractor with variable delays
                mock_extractor = Mock()

                call_count = 0

                def variable_delay_extract(file_path):
                    nonlocal call_count
                    call_count += 1
                    if call_count <= 2:
                        # First two files complete quickly
                        return f"extracted text {call_count}"
                    # Later files timeout
                    import time

                    time.sleep(10)  # Will cause timeout
                    return "should not reach here"

                mock_extractor.extract_text = variable_delay_extract
                mock_get_extractor.return_value = mock_extractor

                results = await runner.run_benchmark_suite()

                # Should have mix of successful and timeout results
                success_count = sum(1 for r in results if r.status == ExtractionStatus.SUCCESS)
                timeout_count = sum(1 for r in results if r.status == ExtractionStatus.TIMEOUT)

                assert success_count > 0, "Should have some successful extractions"
                # Timeout count depends on exact timing, but should handle gracefully

        finally:
            for test_file in test_files:
                test_file.unlink()

    def test_timeout_configuration_consistency(self):
        """Test that timeout configurations are consistent across components."""
        from src.config_defaults import DefaultValues

        # CLI and config should use same default timeout
        config = BenchmarkConfig(
            frameworks=[Framework.KREUZBERG_SYNC],
            categories=[DocumentCategory.TINY],
            output_dir=Path("test_output"),
        )

        # Should use centralized defaults
        assert config.timeout_seconds == DefaultValues.EXTRACTION_TIMEOUT_SECONDS
        assert config.max_run_duration_minutes == DefaultValues.MAX_RUN_DURATION_MINUTES

    @pytest.mark.asyncio
    async def test_warmup_timeout_interaction(self):
        """Test interaction between warmup phase and timeouts."""
        config = BenchmarkConfig(
            frameworks=[Framework.KREUZBERG_SYNC],
            categories=[DocumentCategory.TINY],
            iterations=1,
            warmup_runs=2,
            max_run_duration_minutes=0.03,  # Very short - should timeout during warmup
            output_dir=Path("test_output"),
        )

        runner = ComprehensiveBenchmarkRunner(config)

        with patch.object(runner, "_run_warmup") as mock_warmup:
            # Mock slow warmup
            mock_warmup.side_effect = lambda: asyncio.sleep(10)

            start_time = asyncio.get_event_loop().time()
            results = await runner.run_benchmark_suite()
            end_time = asyncio.get_event_loop().time()

            # Should timeout quickly, even during warmup
            elapsed = end_time - start_time
            assert elapsed < 5  # Should timeout way before 10 seconds


class TestTimeoutErrorHandling:
    """Test error handling specifically related to timeouts."""

    @pytest.mark.asyncio
    async def test_timeout_error_messages(self):
        """Test that timeout errors have informative messages."""
        config = BenchmarkConfig(
            frameworks=[Framework.KREUZBERG_SYNC],
            categories=[DocumentCategory.TINY],
            iterations=1,
            timeout_seconds=1,
            output_dir=Path("test_output"),
        )

        runner = ComprehensiveBenchmarkRunner(config)

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"Timeout test")
            test_file = Path(f.name)

        try:
            with patch("src.benchmark.get_extractor") as mock_get_extractor:
                mock_extractor = Mock()
                mock_extractor.extract_text.side_effect = lambda x: asyncio.sleep(5)
                mock_get_extractor.return_value = mock_extractor

                mock_metadata = {"file_size": 1000, "file_type": "txt"}

                with patch.object(runner.categorizer, "_get_file_metadata") as mock_metadata_func:
                    mock_metadata_func.return_value = mock_metadata

                    result = await runner._benchmark_single_file(
                        Framework.KREUZBERG_SYNC, test_file, mock_metadata, 0, DocumentCategory.TINY
                    )

                    # Check error message quality
                    assert result.status == ExtractionStatus.TIMEOUT
                    assert result.error_type == "TimeoutError"
                    assert "timeout" in result.error_message.lower()
                    assert str(config.timeout_seconds) in result.error_message

        finally:
            test_file.unlink()

    @pytest.mark.asyncio
    async def test_timeout_retry_behavior(self):
        """Test retry behavior when timeouts occur."""
        config = BenchmarkConfig(
            frameworks=[Framework.KREUZBERG_SYNC],
            categories=[DocumentCategory.TINY],
            iterations=1,
            max_retries=2,
            timeout_seconds=1,
            output_dir=Path("test_output"),
        )

        runner = ComprehensiveBenchmarkRunner(config)

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"Retry timeout test")
            test_file = Path(f.name)

        try:
            with patch("src.benchmark.get_extractor") as mock_get_extractor:
                mock_extractor = Mock()

                # Track call count for retries
                call_count = 0

                def counting_extract(file_path):
                    nonlocal call_count
                    call_count += 1
                    # Always timeout
                    import time

                    time.sleep(5)
                    return "should not reach"

                mock_extractor.extract_text = counting_extract
                mock_get_extractor.return_value = mock_extractor

                mock_metadata = {"file_size": 1000, "file_type": "txt"}

                with patch.object(runner.categorizer, "_get_file_metadata") as mock_metadata_func:
                    mock_metadata_func.return_value = mock_metadata

                    result = await runner._benchmark_single_file(
                        Framework.KREUZBERG_SYNC, test_file, mock_metadata, 0, DocumentCategory.TINY
                    )

                    # Should have retried the configured number of times
                    assert result.attempts == config.max_retries
                    assert result.status == ExtractionStatus.TIMEOUT

        finally:
            test_file.unlink()
