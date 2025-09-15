"""Enhanced benchmark runner with comprehensive testing capabilities.

~keep Core benchmarking logic that:
- Runs multiple iterations with warmup/cooldown for statistical significance
- Profiles CPU, memory usage during extraction for each framework
- Handles both sync/async extractors with timeout protection
- Categorizes documents by size/type for fair comparison
- Aggregates results with failure analysis and quality metrics
"""

from __future__ import annotations

import asyncio
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import TYPE_CHECKING, Any, Self

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from src.categorizer import DocumentCategorizer
from src.extractors import get_extractor
from src.profiler import AsyncPerformanceProfiler, profile_performance
from src.types import (
    BenchmarkConfig,
    BenchmarkResult,
    BenchmarkSummary,
    DocumentCategory,
    ExtractionResult,
    ExtractionStatus,
    Framework,
)

if TYPE_CHECKING:
    from src.types import AsyncExtractorProtocol, ExtractorProtocol


class ComprehensiveBenchmarkRunner:
    """~keep Orchestrates multi-iteration benchmarks with resource monitoring.

    Key responsibilities:
    - Run warmup iterations to eliminate cold-start effects
    - Execute multiple benchmark iterations for statistical significance
    - Profile CPU/memory usage during extraction
    - Handle both sync/async extractors uniformly
    - Aggregate results with failure analysis
    """

    def __init__(self, config: BenchmarkConfig) -> None:
        self.config = config
        self.console = Console()
        self.categorizer = DocumentCategorizer()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.results: list[BenchmarkResult] = []
        self.failed_files: dict[str, int] = {}

    def __del__(self) -> None:
        if hasattr(self, "executor") and self.executor is not None:
            try:
                self.executor.shutdown(wait=True)
            except Exception:
                pass

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if hasattr(self, "executor") and self.executor is not None:
            self.executor.shutdown(wait=True)

    def _clear_kreuzberg_cache(self) -> None:
        cache_paths = [
            Path.home() / ".kreuzberg",
            Path.cwd() / ".kreuzberg",
        ]

        for cache_path in cache_paths:
            if cache_path.exists():
                try:
                    shutil.rmtree(cache_path)
                    self.console.print(f"[yellow]Cleared cache: {cache_path}[/yellow]")
                except Exception as e:
                    self.console.print(f"[red]Failed to clear cache {cache_path}: {e}[/red]")

    async def run_benchmark_suite(self) -> list[BenchmarkResult]:
        """~keep Main entry point: run multi-iteration benchmark with warmup/cooldown."""
        start_time = time.time()
        max_duration_seconds = self.config.max_run_duration_minutes * 60

        self.console.print(
            f"[bold blue]Starting comprehensive benchmark suite[/bold blue]\n"
            f"Iterations: {self.config.iterations}\n"
            f"Frameworks: {', '.join(f.value for f in self.config.frameworks)}\n"
            f"Categories: ALL (testing all file sizes and types)\n"
            f"Quality Assessment: {'[green]Enabled[/green]' if self.config.enable_quality_assessment else '[red]Disabled[/red]'}\n"
            f"Max duration: {self.config.max_run_duration_minutes} minutes\n"
        )

        try:
            return await asyncio.wait_for(
                self._run_benchmark_with_timeout_check(start_time, max_duration_seconds),
                timeout=max_duration_seconds,
            )
        except TimeoutError:
            elapsed_minutes = (time.time() - start_time) / 60
            self.console.print(f"[red]❌ Benchmark suite timed out after {elapsed_minutes:.1f} minutes[/red]")
            if self.results:
                await self._save_results()
                self.console.print(f"[yellow]⚠️ Saved {len(self.results)} partial results before timeout[/yellow]")
            return self.results

    async def _run_benchmark_with_timeout_check(
        self, start_time: float, max_duration_seconds: float
    ) -> list[BenchmarkResult]:
        if self.config.warmup_runs > 0:
            self.console.print("\n[yellow]Running warmup iterations...[/yellow]")
            await self._run_warmup()

            if time.time() - start_time > max_duration_seconds:
                self.console.print("[red]❌ Timeout reached during warmup phase[/red]")
                return self.results

        for iteration in range(self.config.iterations):
            elapsed = time.time() - start_time
            if elapsed > max_duration_seconds:
                (max_duration_seconds - elapsed) / 60
                self.console.print(
                    f"[red]❌ Timeout reached before iteration {iteration + 1}. "
                    f"Ran for {elapsed / 60:.1f} minutes[/red]"
                )
                break

            self.console.print(
                f"\n[bold green]Starting iteration {iteration + 1}/{self.config.iterations}[/bold green]"
                f" (elapsed: {elapsed / 60:.1f}min/{self.config.max_run_duration_minutes}min)"
            )

            iteration_results = await self._run_single_iteration(iteration)
            self.results.extend(iteration_results)

            if time.time() - start_time > max_duration_seconds:
                self.console.print("[red]❌ Timeout reached after completing iteration[/red]")
                break

            if iteration < self.config.iterations - 1:
                self.console.print(f"[dim]Cooling down for {self.config.cooldown_seconds} seconds...[/dim]")
                await asyncio.sleep(self.config.cooldown_seconds)

        await self._save_results()
        return self.results

    async def _run_warmup(self) -> None:
        """~keep Run warmup without recording - eliminates cold-start bias."""
        test_files = await self._get_warmup_files()

        for framework in self.config.frameworks:
            for file_path in test_files:
                try:
                    extractor = get_extractor(framework)
                    if asyncio.iscoroutinefunction(extractor.extract_text):
                        await extractor.extract_text(str(file_path))
                    else:
                        await asyncio.get_event_loop().run_in_executor(
                            self.executor, extractor.extract_text, str(file_path)
                        )
                except Exception:
                    pass

    async def _get_warmup_files(self) -> list[Path]:
        warmup_files = []
        test_dir = self.config.output_dir.parent / "test_documents"

        for category in [
            DocumentCategory.TINY,
            DocumentCategory.PDF_STANDARD,
            DocumentCategory.OFFICE,
        ]:
            files = self.categorizer.get_files_for_category(test_dir, category, self.config.table_extraction_only)
            if files:
                warmup_files.append(files[0][0])

        return warmup_files[: self.config.warmup_runs]

    async def _run_single_iteration(self, iteration: int) -> list[BenchmarkResult]:
        iteration_results = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=self.console,
        ) as progress:
            for framework in self.config.frameworks:
                if "kreuzberg" in framework.value.lower():
                    self._clear_kreuzberg_cache()

                framework_task = progress.add_task(f"[cyan]Testing {framework.value}...[/cyan]", total=None)

                for category in self.config.categories:
                    progress.update(
                        framework_task,
                        description=f"[cyan]Testing {framework.value} - {category.value}...[/cyan]",
                    )

                    test_files = await self._get_test_files(category, framework)

                    for file_path, metadata in test_files:
                        if self._should_skip_file(str(file_path)):
                            continue

                        result = await self._benchmark_single_file(framework, file_path, metadata, iteration, category)

                        if result:
                            iteration_results.append(result)

                progress.remove_task(framework_task)

        return iteration_results

    async def _get_test_files(
        self, category: DocumentCategory, framework: Framework | None = None
    ) -> list[tuple[Path, dict[str, Any]]]:
        test_dir = self.config.output_dir.parent / "test_documents"
        files = self.categorizer.get_files_for_category(test_dir, category, self.config.table_extraction_only)

        if framework:
            from .config import should_test_file

            filtered_files = []
            for path, meta in files:
                if should_test_file(str(path), framework):
                    filtered_files.append((path, meta))
            files = filtered_files

        return files

    def _should_skip_file(self, file_path: str) -> bool:
        if not self.config.skip_on_repeated_failure:
            return False

        failure_count = self.failed_files.get(file_path, 0)
        return failure_count >= self.config.max_retries

    async def _benchmark_single_file(
        self,
        framework: Framework,
        file_path: Path,
        metadata: dict[str, Any],
        iteration: int,
        category: DocumentCategory,
    ) -> BenchmarkResult | None:
        if "kreuzberg" in framework.value:
            import shutil

            cache_dir = Path(".kreuzberg")
            if cache_dir.exists():
                shutil.rmtree(cache_dir)

        for attempt in range(self.config.max_retries):
            try:
                extraction_result = await asyncio.wait_for(
                    self._run_extraction(framework, file_path),
                    timeout=self.config.timeout_seconds,
                )

                result = BenchmarkResult(
                    file_path=str(file_path),
                    file_size=metadata["file_size"],
                    file_type=metadata["file_type"],
                    category=category,
                    framework=framework,
                    iteration=iteration,
                    extraction_time=extraction_result.extraction_time or 0,
                    peak_memory_mb=extraction_result.resource_metrics[-1].memory_rss / (1024 * 1024)
                    if extraction_result.resource_metrics
                    else 0,
                    avg_memory_mb=sum(m.memory_rss for m in extraction_result.resource_metrics)
                    / len(extraction_result.resource_metrics)
                    / (1024 * 1024)
                    if extraction_result.resource_metrics
                    else 0,
                    peak_cpu_percent=max(
                        (m.cpu_percent for m in extraction_result.resource_metrics),
                        default=0,
                    ),
                    avg_cpu_percent=sum(m.cpu_percent for m in extraction_result.resource_metrics)
                    / len(extraction_result.resource_metrics)
                    if extraction_result.resource_metrics
                    else 0,
                    status=extraction_result.status,
                    character_count=extraction_result.character_count,
                    word_count=extraction_result.word_count,
                    error_type=extraction_result.error_type,
                    error_message=extraction_result.error_message,
                    extracted_text=extraction_result.extracted_text,
                    extracted_metadata=extraction_result.extracted_metadata,
                    metadata_field_count=len(extraction_result.extracted_metadata)
                    if extraction_result.extracted_metadata
                    else None,
                    attempts=attempt + 1,
                )

                if extraction_result.status == ExtractionStatus.SUCCESS:
                    self.failed_files.pop(str(file_path), None)

                return result

            except TimeoutError:
                if attempt == self.config.max_retries - 1:
                    self.failed_files[str(file_path)] = self.failed_files.get(str(file_path), 0) + 1
                    return BenchmarkResult(
                        file_path=str(file_path),
                        file_size=metadata["file_size"],
                        file_type=metadata["file_type"],
                        category=category,
                        framework=framework,
                        iteration=iteration,
                        extraction_time=self.config.timeout_seconds,
                        peak_memory_mb=0,
                        avg_memory_mb=0,
                        peak_cpu_percent=0,
                        avg_cpu_percent=0,
                        status=ExtractionStatus.TIMEOUT,
                        error_type="TimeoutError",
                        error_message=f"Extraction timed out after {self.config.timeout_seconds} seconds",
                        attempts=attempt + 1,
                    )

            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    self.failed_files[str(file_path)] = self.failed_files.get(str(file_path), 0) + 1

                    if not self.config.continue_on_error:
                        raise

                    return BenchmarkResult(
                        file_path=str(file_path),
                        file_size=metadata["file_size"],
                        file_type=metadata["file_type"],
                        category=category,
                        framework=framework,
                        iteration=iteration,
                        extraction_time=0,
                        peak_memory_mb=0,
                        avg_memory_mb=0,
                        peak_cpu_percent=0,
                        avg_cpu_percent=0,
                        status=ExtractionStatus.FAILED,
                        error_type=type(e).__name__,
                        error_message=str(e) if self.config.detailed_errors else "Extraction failed",
                        extracted_text=None,
                        attempts=attempt + 1,
                    )

            if attempt < self.config.max_retries - 1:
                await asyncio.sleep(self.config.retry_backoff**attempt)

        return None

    async def _run_extraction(self, framework: Framework, file_path: Path) -> ExtractionResult:
        try:
            extractor = get_extractor(framework)

            if asyncio.iscoroutinefunction(extractor.extract_text):
                return await self._run_async_extraction(extractor, file_path, framework)
            return await self._run_sync_extraction(extractor, file_path, framework)

        except Exception as e:
            return ExtractionResult(
                file_path=str(file_path),
                file_size=file_path.stat().st_size if file_path.exists() else 0,
                framework=framework,
                status=ExtractionStatus.FAILED,
                error_type=type(e).__name__,
                error_message=str(e),
            )

    async def _run_async_extraction(
        self, extractor: AsyncExtractorProtocol, file_path: Path, framework: Framework
    ) -> ExtractionResult:
        async with AsyncPerformanceProfiler(self.config.sampling_interval_ms) as metrics:
            start_time = time.time()

            try:
                metadata = None
                if hasattr(extractor, "extract_with_metadata"):
                    text, metadata = await extractor.extract_with_metadata(str(file_path))
                else:
                    text = await extractor.extract_text(str(file_path))

                return ExtractionResult(
                    file_path=str(file_path),
                    file_size=file_path.stat().st_size,
                    framework=framework,
                    status=ExtractionStatus.SUCCESS,
                    extraction_time=time.time() - start_time,
                    extracted_text=text if self.config.save_extracted_text else None,
                    character_count=len(text),
                    word_count=len(text.split()),
                    resource_metrics=metrics.samples,
                    extracted_metadata=metadata,
                )

            except Exception as e:
                return ExtractionResult(
                    file_path=str(file_path),
                    file_size=file_path.stat().st_size if file_path.exists() else 0,
                    framework=framework,
                    status=ExtractionStatus.FAILED,
                    extraction_time=time.time() - start_time,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    resource_metrics=metrics.samples,
                )

    async def _run_sync_extraction(
        self, extractor: ExtractorProtocol, file_path: Path, framework: Framework
    ) -> ExtractionResult:
        def extract_with_profiling() -> ExtractionResult:
            with profile_performance(self.config.sampling_interval_ms) as metrics:
                start_time = time.time()

                try:
                    metadata = None
                    if hasattr(extractor, "extract_with_metadata"):
                        text, metadata = extractor.extract_with_metadata(str(file_path))
                    else:
                        text = extractor.extract_text(str(file_path))

                    return ExtractionResult(
                        file_path=str(file_path),
                        file_size=file_path.stat().st_size,
                        framework=framework,
                        status=ExtractionStatus.SUCCESS,
                        extraction_time=time.time() - start_time,
                        extracted_text=text if self.config.save_extracted_text else None,
                        character_count=len(text),
                        word_count=len(text.split()),
                        resource_metrics=metrics.samples,
                        extracted_metadata=metadata,
                    )

                except Exception as e:
                    return ExtractionResult(
                        file_path=str(file_path),
                        file_size=file_path.stat().st_size if file_path.exists() else 0,
                        framework=framework,
                        status=ExtractionStatus.FAILED,
                        extraction_time=time.time() - start_time,
                        error_type=type(e).__name__,
                        error_message=str(e),
                        resource_metrics=metrics.samples,
                    )

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(self.executor, extract_with_profiling)

        result.framework = framework

        return result

    def _save_results_sync(self) -> None:
        import msgspec

        self.config.output_dir.mkdir(parents=True, exist_ok=True)

        results_path = self.config.output_dir / "benchmark_results.json"
        with open(results_path, "wb") as f:
            f.write(msgspec.json.encode(self.results))

        summaries = self._generate_summaries()
        summaries_path = self.config.output_dir / "benchmark_summaries.json"
        with open(summaries_path, "wb") as f:
            f.write(msgspec.json.encode(summaries))

        self.console.print(f"\n[green]Results saved to {self.config.output_dir}[/green]")

    async def _save_results(self) -> None:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._save_results_sync)

    def _generate_summaries(self) -> list[BenchmarkSummary]:
        import statistics
        from collections import defaultdict

        grouped: dict[tuple[Framework, DocumentCategory], list[BenchmarkResult]] = defaultdict(list)

        for result in self.results:
            key = (result.framework, result.category)
            grouped[key].append(result)

        summaries = []

        for (framework, category), results in grouped.items():
            successful = [r for r in results if r.status == ExtractionStatus.SUCCESS]
            failed = [r for r in results if r.status == ExtractionStatus.FAILED]
            partial = [r for r in results if r.status == ExtractionStatus.PARTIAL]
            timeout = [r for r in results if r.status == ExtractionStatus.TIMEOUT]

            if successful:
                times = [r.extraction_time for r in successful]
                avg_time = statistics.mean(times)
                median_time = statistics.median(times)
                min_time = min(times)
                max_time = max(times)
                std_time = statistics.stdev(times) if len(times) > 1 else 0

                peak_memories = [r.peak_memory_mb for r in successful]
                avg_peak_memory = statistics.mean(peak_memories)

                avg_cpus = [r.avg_cpu_percent for r in successful]
                avg_cpu = statistics.mean(avg_cpus)

                total_time = sum(times)
                total_files = len(successful)
                total_mb = sum(r.file_size for r in successful) / (1024 * 1024)

                files_per_second = total_files / total_time if total_time > 0 else 0
                mb_per_second = total_mb / total_time if total_time > 0 else 0

                char_counts = [r.character_count for r in successful if r.character_count]
                word_counts = [r.word_count for r in successful if r.word_count]

                avg_chars = statistics.mean(char_counts) if char_counts else None
                avg_words = statistics.mean(word_counts) if word_counts else None

                quality_stats = self._calculate_quality_statistics(successful)
            else:
                avg_time = median_time = min_time = max_time = std_time = None
                avg_peak_memory = avg_cpu = None
                files_per_second = mb_per_second = None
                avg_chars = avg_words = None
                quality_stats = None

            summary = BenchmarkSummary(
                framework=framework,
                category=category,
                total_files=len(results),
                successful_files=len(successful),
                failed_files=len(failed),
                partial_files=len(partial),
                timeout_files=len(timeout),
                avg_extraction_time=avg_time,
                median_extraction_time=median_time,
                min_extraction_time=min_time,
                max_extraction_time=max_time,
                std_extraction_time=std_time,
                avg_peak_memory_mb=avg_peak_memory,
                avg_cpu_percent=avg_cpu,
                files_per_second=files_per_second,
                mb_per_second=mb_per_second,
                success_rate=len(successful) / len(results) if results else 0,
                avg_character_count=int(avg_chars) if avg_chars else None,
                avg_word_count=int(avg_words) if avg_words else None,
                avg_quality_score=quality_stats["avg"] if quality_stats else None,
                min_quality_score=quality_stats["min"] if quality_stats else None,
                max_quality_score=quality_stats["max"] if quality_stats else None,
                avg_completeness=quality_stats["completeness"] if quality_stats else None,
                avg_coherence=quality_stats["coherence"] if quality_stats else None,
                avg_readability=quality_stats["readability"] if quality_stats else None,
            )

            summaries.append(summary)

        return summaries

    def _calculate_quality_statistics(self, successful_results: list[BenchmarkResult]) -> dict[str, float] | None:
        import statistics

        quality_scores = [r.overall_quality_score for r in successful_results if r.overall_quality_score is not None]
        if not quality_scores:
            return None

        completeness_scores = []
        coherence_scores = []
        readability_scores = []

        for r in successful_results:
            if r.quality_metrics:
                if "extraction_completeness" in r.quality_metrics:
                    completeness_scores.append(r.quality_metrics["extraction_completeness"])
                if "text_coherence" in r.quality_metrics:
                    coherence_scores.append(r.quality_metrics["text_coherence"])
                if "flesch_reading_ease" in r.quality_metrics:
                    flesch = r.quality_metrics["flesch_reading_ease"]
                    readability_scores.append(min(100, max(0, flesch)) / 100)

        return {
            "avg": statistics.mean(quality_scores),
            "min": min(quality_scores),
            "max": max(quality_scores),
            "completeness": statistics.mean(completeness_scores) if completeness_scores else None,
            "coherence": statistics.mean(coherence_scores) if coherence_scores else None,
            "readability": statistics.mean(readability_scores) if readability_scores else None,
        }
