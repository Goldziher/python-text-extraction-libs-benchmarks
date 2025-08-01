"""Result aggregation for benchmark runs.

~keep Aggregation pipeline that:
- Loads results from multiple framework/category benchmark runs
- Groups by framework/category for statistical analysis
- Calculates speed (files/sec), memory (MB), success rates
- Creates comparison matrices for framework evaluation
- Analyzes failure patterns and performance trends
"""

from __future__ import annotations

import statistics
from collections import defaultdict
from pathlib import Path

import msgspec

from src.types import (
    AggregatedResults,
    BenchmarkResult,
    BenchmarkSummary,
    DocumentCategory,
    ExtractionStatus,
    Framework,
)


class ResultAggregator:
    """~keep Combines benchmark results into statistical summaries.

    Core functions:
    - Load results from distributed CI framework jobs
    - Group by framework/category for fair comparison
    - Calculate speed (files/sec), memory, success rate statistics
    - Generate framework comparison matrices
    """

    def aggregate_results(self, result_dirs: list[Path]) -> AggregatedResults:
        """~keep Main aggregation: combine distributed results into unified metrics."""
        all_results: list[BenchmarkResult] = []

        # Load results from distributed framework/category jobs
        for result_dir in result_dirs:
            results = self._load_results(result_dir)
            all_results.extend(results)

        # Group and calculate statistical summaries
        return self._calculate_aggregated_metrics(all_results)

    def _load_results(self, result_dir: Path) -> list[BenchmarkResult]:
        """~keep Load benchmark results with error handling for partial CI failures."""
        results_file = result_dir / "benchmark_results.json"
        if not results_file.exists():
            return []

        try:
            with open(results_file, "rb") as f:
                data = f.read()
                if not data or len(data) == 0:
                    print(f"Warning: Empty results file: {results_file}")
                    return []
                # Deserialize structured benchmark results from CI artifacts
                return msgspec.json.decode(data, type=list[BenchmarkResult])
        except Exception as e:
            print(f"Error loading {results_file}: {e}")
            return []

    def _calculate_aggregated_metrics(self, results: list[BenchmarkResult]) -> AggregatedResults:
        """~keep Core aggregation: transform raw results into statistical summaries."""
        if not results:
            return self._empty_aggregated_results()

        # Group results by framework and category for fair comparison analysis
        framework_summaries = self._group_by_framework(results)  # Speed/memory by framework
        category_summaries = self._group_by_category(results)  # Performance by file size
        framework_category_matrix = self._create_matrix(results)  # Framework vs category grid

        # Failure analysis for debugging problematic files/frameworks
        failure_patterns = self._analyze_failures(results)
        timeout_files = [r.file_path for r in results if r.status == ExtractionStatus.TIMEOUT]

        # Performance trends across iterations (detect variance/instability)
        performance_trends = self._calculate_performance_trends(results)

        # Platform-specific results (Linux CI vs local testing)
        platform_results = self._group_by_platform(results)

        # Overall benchmark statistics
        total_runs = len({(r.iteration, r.framework) for r in results})  # Unique run combinations
        total_files = len(results)  # Total individual file extractions
        total_time = sum(r.extraction_time for r in results)  # Cumulative processing time

        return AggregatedResults(
            total_runs=total_runs,
            total_files_processed=total_files,
            total_time_seconds=total_time,
            framework_summaries=framework_summaries,
            category_summaries=category_summaries,
            framework_category_matrix=framework_category_matrix,
            failure_patterns=failure_patterns,
            timeout_files=timeout_files,
            performance_over_iterations=performance_trends,
            platform_results=platform_results,
        )

    def _group_by_framework(self, results: list[BenchmarkResult]) -> dict[Framework, list[BenchmarkSummary]]:
        """Group results by framework."""
        grouped = defaultdict(list)

        for framework in Framework:
            framework_results = [r for r in results if r.framework == framework]
            if framework_results:
                # Group by category for this framework
                for category in DocumentCategory:
                    cat_results = [r for r in framework_results if r.category == category]
                    if cat_results:
                        summary = self._create_summary(framework, category, cat_results)
                        grouped[framework].append(summary)

        return dict(grouped)

    def _group_by_category(self, results: list[BenchmarkResult]) -> dict[DocumentCategory, list[BenchmarkSummary]]:
        """Group results by category."""
        grouped = defaultdict(list)

        for category in DocumentCategory:
            category_results = [r for r in results if r.category == category]
            if category_results:
                # Group by framework for this category
                for framework in Framework:
                    fw_results = [r for r in category_results if r.framework == framework]
                    if fw_results:
                        summary = self._create_summary(framework, category, fw_results)
                        grouped[category].append(summary)

        return dict(grouped)

    def _create_matrix(self, results: list[BenchmarkResult]) -> dict[str, BenchmarkSummary]:
        """Create framework/category cross-tabulation matrix."""
        matrix = {}

        for framework in Framework:
            for category in DocumentCategory:
                cell_results = [r for r in results if r.framework == framework and r.category == category]
                if cell_results:
                    summary = self._create_summary(framework, category, cell_results)
                    # Use string key format: "framework_category"
                    key = f"{framework.value}_{category.value}"
                    matrix[key] = summary

        return matrix

    def _create_summary(
        self, framework: Framework, category: DocumentCategory, results: list[BenchmarkResult]
    ) -> BenchmarkSummary:
        """~key Create statistical summary for framework/category - core metrics for comparison."""
        successful = [r for r in results if r.status == ExtractionStatus.SUCCESS]
        failed = [r for r in results if r.status == ExtractionStatus.FAILED]
        partial = [r for r in results if r.status == ExtractionStatus.PARTIAL]
        timeout = [r for r in results if r.status == ExtractionStatus.TIMEOUT]

        # Timing statistics - only use successful extractions to avoid skewing averages
        if successful:
            times = [r.extraction_time for r in successful]
            avg_time = statistics.mean(times)
            median_time = statistics.median(times)  # Robust to outliers
            min_time = min(times)
            max_time = max(times)
            std_time = statistics.stdev(times) if len(times) > 1 else 0  # Measure variance

            # Resource usage statistics
            peak_memories = [r.peak_memory_mb for r in successful]
            avg_peak_memory = statistics.mean(peak_memories)

            avg_cpus = [r.avg_cpu_percent for r in successful]
            avg_cpu = statistics.mean(avg_cpus)

            # Key performance metrics for website tables
            total_time = sum(times)
            total_files = len(successful)
            total_mb = sum(r.file_size for r in successful) / (1024 * 1024)

            files_per_second = total_files / total_time if total_time > 0 else 0  # Primary speed metric
            mb_per_second = total_mb / total_time if total_time > 0 else 0  # Data throughput

            # Text extraction quality metrics
            char_counts = [r.character_count for r in successful if r.character_count]
            word_counts = [r.word_count for r in successful if r.word_count]

            avg_chars = int(statistics.mean(char_counts)) if char_counts else None
            avg_words = int(statistics.mean(word_counts)) if word_counts else None
        else:
            # No successful extractions - all metrics are null
            avg_time = median_time = min_time = max_time = std_time = None
            avg_peak_memory = avg_cpu = None
            files_per_second = mb_per_second = None
            avg_chars = avg_words = None

        return BenchmarkSummary(
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
            avg_character_count=avg_chars,
            avg_word_count=avg_words,
        )

    def _analyze_failures(self, results: list[BenchmarkResult]) -> dict[str, int]:
        """Analyze failure patterns."""
        failures = defaultdict(int)

        for result in results:
            if result.status == ExtractionStatus.FAILED and result.error_type:
                failures[result.error_type] += 1

        return dict(failures)

    def _calculate_performance_trends(self, results: list[BenchmarkResult]) -> dict[Framework, list[float]]:
        """Calculate performance trends over iterations."""
        trends = defaultdict(lambda: defaultdict(list))

        # Group by framework and iteration
        for result in results:
            if result.status == ExtractionStatus.SUCCESS:
                trends[result.framework][result.iteration].append(result.extraction_time)

        # Calculate average per iteration
        performance_trends = {}
        for framework, iterations in trends.items():
            iteration_avgs = []
            for i in sorted(iterations.keys()):
                times = iterations[i]
                iteration_avgs.append(statistics.mean(times))
            performance_trends[framework] = iteration_avgs

        return dict(performance_trends)

    def _group_by_platform(self, results: list[BenchmarkResult]) -> dict[str, dict[Framework, BenchmarkSummary]]:
        """Group results by platform."""
        platform_groups = defaultdict(list)

        # Group results by platform
        for result in results:
            platform_groups[result.platform].append(result)

        # Create summaries for each platform
        platform_results = {}
        for platform, platform_res in platform_groups.items():
            framework_summaries = {}
            for framework in Framework:
                fw_results = [r for r in platform_res if r.framework == framework]
                if fw_results:
                    # Create an aggregate summary across all categories
                    summary = self._create_platform_summary(framework, fw_results)
                    framework_summaries[framework] = summary
            platform_results[platform] = framework_summaries

        return platform_results

    def _create_platform_summary(self, framework: Framework, results: list[BenchmarkResult]) -> BenchmarkSummary:
        """Create a platform-specific summary across all categories."""
        # Use TINY as a placeholder category for platform-wide summaries
        return self._create_summary(framework, DocumentCategory.TINY, results)

    def _empty_aggregated_results(self) -> AggregatedResults:
        """Create empty aggregated results."""
        return AggregatedResults(
            total_runs=0,
            total_files_processed=0,
            total_time_seconds=0,
            framework_summaries={},
            category_summaries={},
            framework_category_matrix={},
            failure_patterns={},
            timeout_files=[],
            performance_over_iterations={},
            platform_results={},
        )

    def save_results(self, aggregated: AggregatedResults, output_dir: Path) -> None:
        """Save aggregated results to disk."""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save as msgspec JSON
        results_path = output_dir / "aggregated_results.json"
        with open(results_path, "wb") as f:
            f.write(msgspec.json.encode(aggregated))

        # Also save summaries separately for easier access
        summaries = []
        for fw_summaries in aggregated.framework_summaries.values():
            summaries.extend(fw_summaries)

        summaries_path = output_dir / "all_summaries.json"
        with open(summaries_path, "wb") as f:
            f.write(msgspec.json.encode(summaries))
