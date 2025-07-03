"""Core benchmarking functionality."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

if sys.version_info >= (3, 13):
    pass
else:
    pass

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from .extractors import get_extractor
from .profiler import AsyncPerformanceProfiler, profile_performance
from .types import (
    AsyncExtractorProtocol,
    BenchmarkResult,
    BenchmarkSummary,
    ExtractorProtocol,
    FileType,
    Framework,
)

console = Console()


class BenchmarkRunner:
    """Main benchmark runner for text extraction frameworks."""

    def __init__(
        self,
        frameworks: list[Framework] | None = None,
        file_types: list[FileType] | None = None,
        timeout_seconds: int = 300,
    ) -> None:
        """Initialize benchmark runner.

        Args:
            frameworks: List of frameworks to benchmark. Defaults to all.
            file_types: List of file types to test. Defaults to all.
            timeout_seconds: Timeout for each extraction attempt.
        """
        self.frameworks = frameworks or list(Framework)
        self.file_types = file_types or list(FileType)
        self.timeout_seconds = timeout_seconds
        self.results: list[BenchmarkResult] = []

    async def run_benchmarks(self, test_files_dir: str | Path) -> list[BenchmarkResult]:
        """Run benchmarks for all frameworks and file types.

        Args:
            test_files_dir: Directory containing test files.

        Returns:
            List of benchmark results.
        """
        test_files_path = Path(test_files_dir)
        if not test_files_path.exists():
            msg = f"Test files directory does not exist: {test_files_dir}"
            raise ValueError(msg)

        # Collect test files
        test_files = self._collect_test_files(test_files_path)
        if not test_files:
            msg = f"No test files found in: {test_files_dir}"
            raise ValueError(msg)

        console.print(f"Found {len(test_files)} test files")
        console.print(f"Testing {len(self.frameworks)} frameworks")

        total_runs = len(self.frameworks) * len(test_files)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Running benchmarks...", total=total_runs)

            for framework in self.frameworks:
                for file_path in test_files:
                    file_type = self._get_file_type(file_path)
                    if file_type not in self.file_types:
                        progress.advance(task)
                        continue

                    progress.update(
                        task,
                        description=f"Testing {framework.value} on {file_path.name}",
                    )

                    result = await self._run_single_benchmark(framework, file_path, file_type)
                    self.results.append(result)
                    progress.advance(task)

        return self.results

    async def _run_single_benchmark(
        self,
        framework: Framework,
        file_path: Path,
        file_type: FileType,
    ) -> BenchmarkResult:
        """Run a single benchmark for a framework and file.

        Args:
            framework: The framework to test.
            file_path: Path to the test file.
            file_type: Type of the file.

        Returns:
            Benchmark result.
        """
        file_size = file_path.stat().st_size

        try:
            extractor = get_extractor(framework.value)

            if framework in {Framework.KREUZBERG_ASYNC}:
                return await self._run_async_benchmark(framework, extractor, file_path, file_type, file_size)  # type: ignore[arg-type]
            return await self._run_sync_benchmark(framework, extractor, file_path, file_type, file_size)  # type: ignore[arg-type]

        except Exception as e:
            return BenchmarkResult(
                framework=framework,
                file_type=file_type,
                file_path=str(file_path),
                file_size_bytes=file_size,
                extraction_time_seconds=0.0,
                memory_peak_mb=0.0,
                cpu_percent=0.0,
                success=False,
                error_message=str(e),
            )

    async def _run_async_benchmark(
        self,
        framework: Framework,
        extractor: AsyncExtractorProtocol,
        file_path: Path,
        file_type: FileType,
        file_size: int,
    ) -> BenchmarkResult:
        """Run benchmark for async extractor."""
        try:
            profiler = AsyncPerformanceProfiler()
            async with profiler as metrics:
                extracted_text = await asyncio.wait_for(
                    extractor.extract_text(str(file_path)),
                    timeout=self.timeout_seconds,
                )

            return BenchmarkResult(
                framework=framework,
                file_type=file_type,
                file_path=str(file_path),
                file_size_bytes=file_size,
                extraction_time_seconds=metrics.duration_seconds,
                memory_peak_mb=metrics.memory_peak_mb,
                cpu_percent=metrics.average_cpu_percent,
                success=True,
                extracted_text_length=len(extracted_text),
                extracted_text_preview=extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text,
            )

        except TimeoutError:
            return BenchmarkResult(
                framework=framework,
                file_type=file_type,
                file_path=str(file_path),
                file_size_bytes=file_size,
                extraction_time_seconds=self.timeout_seconds,
                memory_peak_mb=0.0,
                cpu_percent=0.0,
                success=False,
                error_message=f"Timeout after {self.timeout_seconds} seconds",
            )

    async def _run_sync_benchmark(
        self,
        framework: Framework,
        extractor: ExtractorProtocol,
        file_path: Path,
        file_type: FileType,
        file_size: int,
    ) -> BenchmarkResult:
        """Run benchmark for sync extractor in async context."""
        try:
            # Run sync extraction in thread pool to avoid blocking
            def run_extraction() -> tuple[str, float, float, float]:
                with profile_performance() as metrics:
                    extracted_text = extractor.extract_text(str(file_path))
                return (
                    extracted_text,
                    metrics.duration_seconds,
                    metrics.memory_peak_mb,
                    metrics.average_cpu_percent,
                )

            extracted_text, duration, memory_peak, cpu_avg = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, run_extraction),
                timeout=self.timeout_seconds,
            )

            return BenchmarkResult(
                framework=framework,
                file_type=file_type,
                file_path=str(file_path),
                file_size_bytes=file_size,
                extraction_time_seconds=duration,
                memory_peak_mb=memory_peak,
                cpu_percent=cpu_avg,
                success=True,
                extracted_text_length=len(extracted_text),
                extracted_text_preview=extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text,
            )

        except TimeoutError:
            return BenchmarkResult(
                framework=framework,
                file_type=file_type,
                file_path=str(file_path),
                file_size_bytes=file_size,
                extraction_time_seconds=self.timeout_seconds,
                memory_peak_mb=0.0,
                cpu_percent=0.0,
                success=False,
                error_message=f"Timeout after {self.timeout_seconds} seconds",
            )

    def _collect_test_files(self, test_files_dir: Path) -> list[Path]:
        """Collect test files from directory.

        Args:
            test_files_dir: Directory to search for test files.

        Returns:
            List of test file paths.
        """
        supported_extensions = {".pdf", ".docx", ".pptx", ".xlsx", ".html", ".htm", ".md", ".txt"}

        test_files: list[Path] = []
        for ext in supported_extensions:
            test_files.extend(test_files_dir.glob(f"**/*{ext}"))

        return sorted(test_files)

    def _get_file_type(self, file_path: Path) -> FileType:
        """Determine file type from file path.

        Args:
            file_path: Path to the file.

        Returns:
            FileType enum value.

        Raises:
            ValueError: If file type is not supported.
        """
        suffix = file_path.suffix.lower()
        mapping = {
            ".pdf": FileType.PDF,
            ".docx": FileType.DOCX,
            ".pptx": FileType.PPTX,
            ".xlsx": FileType.XLSX,
            ".html": FileType.HTML,
            ".htm": FileType.HTML,
            ".md": FileType.MARKDOWN,
            ".txt": FileType.TXT,
        }

        if suffix not in mapping:
            msg = f"Unsupported file type: {suffix}"
            raise ValueError(msg)

        return mapping[suffix]

    def generate_summary(self) -> list[BenchmarkSummary]:
        """Generate summary statistics from benchmark results.

        Returns:
            List of benchmark summaries grouped by framework and file type.
        """
        summaries = []

        # Group results by framework and file type
        groups: dict[tuple[Framework, FileType], list[BenchmarkResult]] = {}
        for result in self.results:
            key = (result.framework, result.file_type)
            if key not in groups:
                groups[key] = []
            groups[key].append(result)

        # Generate summary for each group
        for (framework, file_type), group_results in groups.items():
            successful = [r for r in group_results if r.success]
            failed = [r for r in group_results if not r.success]

            if successful:
                times = [r.extraction_time_seconds for r in successful]
                memories = [r.memory_peak_mb for r in successful]
                cpus = [r.cpu_percent for r in successful]

                summary = BenchmarkSummary(
                    framework=framework,
                    file_type=file_type,
                    total_files=len(group_results),
                    successful_extractions=len(successful),
                    failed_extractions=len(failed),
                    average_time_seconds=sum(times) / len(times),
                    median_time_seconds=sorted(times)[len(times) // 2],
                    min_time_seconds=min(times),
                    max_time_seconds=max(times),
                    average_memory_mb=sum(memories) / len(memories),
                    average_cpu_percent=sum(cpus) / len(cpus),
                    total_time_seconds=sum(times),
                )
            else:
                summary = BenchmarkSummary(
                    framework=framework,
                    file_type=file_type,
                    total_files=len(group_results),
                    successful_extractions=0,
                    failed_extractions=len(failed),
                    average_time_seconds=0.0,
                    median_time_seconds=0.0,
                    min_time_seconds=0.0,
                    max_time_seconds=0.0,
                    average_memory_mb=0.0,
                    average_cpu_percent=0.0,
                    total_time_seconds=0.0,
                )

            summaries.append(summary)

        return summaries
