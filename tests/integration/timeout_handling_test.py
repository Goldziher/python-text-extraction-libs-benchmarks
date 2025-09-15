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
    @pytest.mark.asyncio
    async def test_benchmark_suite_timeout_short_duration(self):
        config = BenchmarkConfig(
            frameworks=[Framework.KREUZBERG_SYNC],
            categories=[DocumentCategory.TINY],
            iterations=1,
            warmup_runs=0,
            max_run_duration_minutes=0.02,
            output_dir=Path("test_output"),
        )

        runner = ComprehensiveBenchmarkRunner(config)

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"Test content")
            test_file = Path(f.name)

        try:
            with (
                patch.object(runner.categorizer, "get_files_by_category") as mock_get_files,
                patch("src.benchmark.get_extractor") as mock_get_extractor,
            ):
                mock_get_files.return_value = [test_file]

                mock_extractor = Mock()
                mock_extractor.extract_text.side_effect = lambda x: asyncio.sleep(10)
                mock_get_extractor.return_value = mock_extractor

                start_time = asyncio.get_event_loop().time()
                results = await runner.run_benchmark_suite()
                end_time = asyncio.get_event_loop().time()

                elapsed_seconds = end_time - start_time
                assert elapsed_seconds < 5

                assert isinstance(results, list)

        finally:
            test_file.unlink()

    @pytest.mark.asyncio
    async def test_individual_file_timeout(self):
        config = BenchmarkConfig(
            frameworks=[Framework.KREUZBERG_SYNC],
            categories=[DocumentCategory.TINY],
            iterations=1,
            warmup_runs=0,
            timeout_seconds=1,
            output_dir=Path("test_output"),
        )

        runner = ComprehensiveBenchmarkRunner(config)

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"Test content for timeout testing")
            test_file = Path(f.name)

        try:
            with patch("src.benchmark.get_extractor") as mock_get_extractor:
                mock_extractor = Mock()

                async def slow_extract(file_path):
                    await asyncio.sleep(5)
                    return "extracted text"

                mock_extractor.extract_text = slow_extract
                mock_get_extractor.return_value = mock_extractor

                mock_metadata = {
                    "file_size": 1000,
                    "file_type": "txt",
                }

                with patch.object(runner.categorizer, "_get_file_metadata") as mock_metadata_func:
                    mock_metadata_func.return_value = mock_metadata

                    result = await runner._benchmark_single_file(
                        Framework.KREUZBERG_SYNC, test_file, mock_metadata, 0, DocumentCategory.TINY
                    )

                    assert result is not None
                    assert result.status == ExtractionStatus.TIMEOUT
                    assert "timeout" in result.error_message.lower()

        finally:
            test_file.unlink()

    @pytest.mark.asyncio
    async def test_timeout_recovery_and_partial_results(self):
        config = BenchmarkConfig(
            frameworks=[Framework.KREUZBERG_SYNC],
            categories=[DocumentCategory.TINY],
            iterations=2,
            warmup_runs=0,
            max_run_duration_minutes=0.05,
            output_dir=Path("test_output"),
        )

        runner = ComprehensiveBenchmarkRunner(config)

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

                mock_extractor = Mock()

                call_count = 0

                async def variable_speed_extract(file_path):
                    nonlocal call_count
                    call_count += 1
                    if call_count == 1:
                        await asyncio.sleep(0.1)
                        return "extracted text 1"
                    await asyncio.sleep(10)
                    return "extracted text slow"

                mock_extractor.extract_text = variable_speed_extract
                mock_get_extractor.return_value = mock_extractor

                results = await runner.run_benchmark_suite()

                mock_save.assert_called()

        finally:
            for test_file in test_files:
                test_file.unlink()

    @pytest.mark.asyncio
    async def test_async_extractor_timeout_handling(self):
        config = BenchmarkConfig(
            frameworks=[Framework.KREUZBERG_ASYNC],
            categories=[DocumentCategory.TINY],
            iterations=1,
            warmup_runs=0,
            timeout_seconds=1,
            output_dir=Path("test_output"),
        )

        runner = ComprehensiveBenchmarkRunner(config)

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"Test async timeout")
            test_file = Path(f.name)

        try:
            with patch("src.benchmark.get_extractor") as mock_get_extractor:
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
        config = BenchmarkConfig(
            frameworks=[Framework.KREUZBERG_SYNC],
            categories=[DocumentCategory.TINY],
            iterations=1,
            warmup_runs=0,
            timeout_seconds=2,
            concurrent_files=2,
            output_dir=Path("test_output"),
        )

        runner = ComprehensiveBenchmarkRunner(config)

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

                mock_extractor = Mock()

                call_count = 0

                def variable_delay_extract(file_path):
                    nonlocal call_count
                    call_count += 1
                    if call_count <= 2:
                        return f"extracted text {call_count}"
                    import time

                    time.sleep(10)
                    return "should not reach here"

                mock_extractor.extract_text = variable_delay_extract
                mock_get_extractor.return_value = mock_extractor

                results = await runner.run_benchmark_suite()

                success_count = sum(1 for r in results if r.status == ExtractionStatus.SUCCESS)
                timeout_count = sum(1 for r in results if r.status == ExtractionStatus.TIMEOUT)

                assert success_count > 0, "Should have some successful extractions"

        finally:
            for test_file in test_files:
                test_file.unlink()

    def test_timeout_configuration_consistency(self):
        from src.config_defaults import DefaultValues

        config = BenchmarkConfig(
            frameworks=[Framework.KREUZBERG_SYNC],
            categories=[DocumentCategory.TINY],
            output_dir=Path("test_output"),
        )

        assert config.timeout_seconds == DefaultValues.EXTRACTION_TIMEOUT_SECONDS
        assert config.max_run_duration_minutes == DefaultValues.MAX_RUN_DURATION_MINUTES

    @pytest.mark.asyncio
    async def test_warmup_timeout_interaction(self):
        config = BenchmarkConfig(
            frameworks=[Framework.KREUZBERG_SYNC],
            categories=[DocumentCategory.TINY],
            iterations=1,
            warmup_runs=2,
            max_run_duration_minutes=0.03,
            output_dir=Path("test_output"),
        )

        runner = ComprehensiveBenchmarkRunner(config)

        with patch.object(runner, "_run_warmup") as mock_warmup:
            mock_warmup.side_effect = lambda: asyncio.sleep(10)

            start_time = asyncio.get_event_loop().time()
            results = await runner.run_benchmark_suite()
            end_time = asyncio.get_event_loop().time()

            elapsed = end_time - start_time
            assert elapsed < 5


class TestTimeoutErrorHandling:
    @pytest.mark.asyncio
    async def test_timeout_error_messages(self):
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

                    assert result.status == ExtractionStatus.TIMEOUT
                    assert result.error_type == "TimeoutError"
                    assert "timeout" in result.error_message.lower()
                    assert str(config.timeout_seconds) in result.error_message

        finally:
            test_file.unlink()

    @pytest.mark.asyncio
    async def test_timeout_retry_behavior(self):
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

                call_count = 0

                def counting_extract(file_path):
                    nonlocal call_count
                    call_count += 1
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

                    assert result.attempts == config.max_retries
                    assert result.status == ExtractionStatus.TIMEOUT

        finally:
            test_file.unlink()
