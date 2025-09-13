"""Generate MkDocs pages from benchmark results."""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import msgspec

from src.types import AggregatedResults, BenchmarkSummary


class DocsGenerator:
    """Generate MkDocs documentation from benchmark results."""

    def __init__(self, docs_dir: Path = Path("docs")) -> None:
        self.docs_dir = docs_dir
        self.results_dir = docs_dir / "results"
        self.assets_dir = self.results_dir / "assets"

    def generate_from_results(self, aggregated_file: Path, charts_dir: Path | None = None) -> None:
        """Generate all documentation pages from aggregated results."""
        with open(aggregated_file, "rb") as f:
            aggregated = msgspec.json.decode(f.read(), type=AggregatedResults)

        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.assets_dir.mkdir(parents=True, exist_ok=True)

        if charts_dir and charts_dir.exists():
            self._copy_charts(charts_dir)

        self._generate_results_index(aggregated)
        self._generate_performance_pages(aggregated)
        self._generate_format_pages(aggregated)
        self._generate_interactive_pages(aggregated)

    def _copy_charts(self, charts_dir: Path) -> None:
        """Copy chart files to docs assets."""
        import shutil

        charts_dest = self.assets_dir / "charts"
        charts_dest.mkdir(exist_ok=True)

        if charts_dir.exists():
            for chart_file in charts_dir.glob("*.png"):
                shutil.copy2(chart_file, charts_dest / chart_file.name)

            for chart_file in charts_dir.glob("*.html"):
                shutil.copy2(chart_file, charts_dest / chart_file.name)

    def _generate_results_index(self, aggregated: AggregatedResults) -> None:
        """Generate main results index page."""
        all_summaries = []
        for summaries_list in aggregated.framework_summaries.values():
            all_summaries.extend(summaries_list)

        frameworks = {s.framework for s in all_summaries}
        total_files = sum(s.total_files for s in all_summaries)
        total_successful = sum(s.successful_files for s in all_summaries)
        overall_success_rate = (total_successful / total_files * 100) if total_files > 0 else 0

        framework_stats = self._calculate_framework_stats(aggregated)

        content = f"""---
title: Latest Benchmark Results
description: Comprehensive performance analysis of text extraction frameworks
---

# Latest Benchmark Results

!!! info "Benchmark Overview"
    **Generated**: {datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")}
    **Frameworks**: {len(frameworks)}
    **Test Files**: {total_files:,}
    **Overall Success Rate**: {overall_success_rate:.1f}%

## 🏆 Performance Rankings

### By Speed (Files/Second)
| Rank | Framework | Files/Sec | Success Rate | Memory (MB) |
|------|-----------|-----------|--------------|-------------|
{self._generate_ranking_table(framework_stats, "speed")}

### By Memory Efficiency
| Rank | Framework | Memory (MB) | Files/Sec | Success Rate |
|------|-----------|-------------|-----------|--------------|
{self._generate_ranking_table(framework_stats, "memory")}

### By Success Rate
| Rank | Framework | Success Rate | Files/Sec | Memory (MB) |
|------|-----------|--------------|-----------|-------------|
{self._generate_ranking_table(framework_stats, "success")}

## 📊 Performance Overview

![Performance Comparison](assets/charts/performance_comparison_large.png)

## 📈 Key Insights

{self._generate_insights(framework_stats)}

## 📋 Detailed Analysis

Explore specific aspects of the benchmark results:

- **[Speed Analysis](performance/speed.md)** - Detailed speed comparisons
- **[Memory Analysis](performance/memory.md)** - Resource usage patterns
- **[Format Support](formats/index.md)** - File format compatibility
- **[Interactive Dashboard](interactive/dashboard.md)** - Explore the data yourself

---

*Data updated: {datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")}*
"""

        with open(self.results_dir / "index.md", "w") as f:
            f.write(content)

    def _calculate_framework_stats(self, aggregated: AggregatedResults) -> dict[str, dict[str, Any]]:
        """Calculate summary statistics for each framework."""
        stats: dict[str, dict[str, Any]] = {}

        all_summaries: list[BenchmarkSummary] = []
        for summaries_list in aggregated.framework_summaries.values():
            all_summaries.extend(summaries_list)

        for summary in all_summaries:
            fw = summary.framework.value if hasattr(summary.framework, "value") else str(summary.framework)
            if fw not in stats:
                stats[fw] = {
                    "total_files": 0,
                    "successful": 0,
                    "times": [],
                    "memory": [],
                    "throughputs": [],
                }

            stats[fw]["total_files"] += summary.total_files
            stats[fw]["successful"] += summary.successful_files

            if summary.avg_extraction_time:
                stats[fw]["times"].append(summary.avg_extraction_time)
            if summary.avg_peak_memory_mb:
                stats[fw]["memory"].append(summary.avg_peak_memory_mb)
            if summary.files_per_second:
                stats[fw]["throughputs"].append(summary.files_per_second)

        for fw_stats in stats.values():
            fw_stats["avg_speed"] = (
                sum(fw_stats["throughputs"]) / len(fw_stats["throughputs"]) if fw_stats["throughputs"] else 0
            )
            fw_stats["avg_memory"] = sum(fw_stats["memory"]) / len(fw_stats["memory"]) if fw_stats["memory"] else 0
            fw_stats["success_rate"] = (
                (fw_stats["successful"] / fw_stats["total_files"] * 100) if fw_stats["total_files"] > 0 else 0
            )

        return stats

    def _generate_ranking_table(self, stats: dict[str, dict[str, Any]], sort_by: str) -> str:
        """Generate ranking table rows."""
        if sort_by == "speed":
            sorted_frameworks = sorted(stats.items(), key=lambda x: x[1]["avg_speed"], reverse=True)
        elif sort_by == "memory":
            sorted_frameworks = sorted(stats.items(), key=lambda x: x[1]["avg_memory"])
        else:
            sorted_frameworks = sorted(stats.items(), key=lambda x: x[1]["success_rate"], reverse=True)

        rows = []
        for rank, (fw, fw_stats) in enumerate(sorted_frameworks, 1):
            rows.append(
                f"| {rank} | **{fw}** | "
                f"{fw_stats['avg_speed']:.2f} | "
                f"{fw_stats['success_rate']:.1f}% | "
                f"{fw_stats['avg_memory']:.0f} |"
            )

        return "\n".join(rows)

    def _generate_insights(self, stats: dict[str, dict[str, Any]]) -> str:
        """Generate key insights from the data."""
        if not stats:
            return """
!!! info "No Data"
    No benchmark data available to generate insights.
"""

        fastest = max(stats.items(), key=lambda x: x[1]["avg_speed"])
        most_efficient = min(stats.items(), key=lambda x: x[1]["avg_memory"])
        most_reliable = max(stats.items(), key=lambda x: x[1]["success_rate"])

        return f"""
!!! success "Speed Champion"
    **{fastest[0]}** leads in processing speed at {fastest[1]["avg_speed"]:.1f} files/second

!!! tip "Memory Efficient"
    **{most_efficient[0]}** uses the least memory at {most_efficient[1]["avg_memory"]:.0f}MB average

!!! check "Most Reliable"
    **{most_reliable[0]}** achieves {most_reliable[1]["success_rate"]:.1f}% success rate
"""

    def _generate_performance_pages(self, aggregated: AggregatedResults) -> None:
        """Generate performance analysis pages."""
        perf_dir = self.results_dir / "performance"
        perf_dir.mkdir(exist_ok=True)

        speed_content = """---
title: Speed Analysis
description: Detailed analysis of extraction speed performance
---

# Speed Performance Analysis

## Extraction Speed Comparison

![Speed Comparison](../assets/charts/performance_comparison_large.png)

## Throughput Analysis

![Throughput Analysis](../assets/charts/throughput_analysis_comprehensive.png)

## Speed by File Size Category

![Performance by Size](../assets/charts/performance_by_size_category.png)

## Key Findings

- **Kreuzberg** consistently leads in speed across all file sizes
- **MarkItDown** shows strong performance on document formats
- **Docling** prioritizes quality over speed with ML processing
- **Extractous** and **Unstructured** offer balanced performance

"""

        with open(perf_dir / "speed.md", "w") as f:
            f.write(speed_content)

        memory_content = """---
title: Memory Usage Analysis
description: Resource usage patterns and memory efficiency
---

# Memory Usage Analysis

## Resource Usage Heatmap

![Memory Usage](../assets/charts/resource_usage_heatmaps.png)

## Memory Efficiency Comparison

The memory footprint varies significantly between frameworks:

- **Kreuzberg Async**: Minimal memory usage (0MB average)
- **Kreuzberg Sync**: Efficient processing (~260MB)
- **MarkItDown**: Moderate usage (~264MB)
- **Extractous**: Higher but manageable (~410MB)
- **Unstructured**: Heavy processing (~1.4GB)
- **Docling**: ML models require significant memory (~1.7GB)

## Memory vs Performance Trade-offs

![Category Analysis](../assets/charts/category_analysis_comprehensive.png)

"""

        with open(perf_dir / "memory.md", "w") as f:
            f.write(memory_content)

    def _generate_format_pages(self, aggregated: AggregatedResults) -> None:
        """Generate format-specific analysis pages."""
        formats_dir = self.results_dir / "formats"
        formats_dir.mkdir(exist_ok=True)

        category_insights = self._generate_category_format_insights(aggregated)

        overview_content = f"""---
title: File Format Analysis
description: Performance analysis by file format
---

# File Format Support Analysis

## Format Coverage

Multiple file formats tested across all frameworks including PDF, DOCX, PPTX, images, and data formats.

## Category-Based Analysis

{category_insights}

## Format-Specific Insights

### Document Formats (.pdf, .docx, .pptx)
- **PDF**: Most challenging format, best handled by Docling and Kreuzberg
- **DOCX**: Generally well supported across frameworks
- **PPTX**: Good support with varying extraction quality

### Image Formats (.png, .jpg, .bmp)
- Requires OCR capabilities
- Kreuzberg and Unstructured show strong OCR performance
- Processing time varies significantly with image complexity

### Data Formats (.csv, .json, .yaml)
- Simple formats with high success rates
- Fast processing across most frameworks
- Format-specific parsing optimizations matter

"""

        with open(formats_dir / "index.md", "w") as f:
            f.write(overview_content)

    def _generate_category_format_insights(self, aggregated: AggregatedResults) -> str:
        """Generate insights based on categories (which relate to formats)."""
        insights = []

        for category, summaries_list in aggregated.category_summaries.items():
            if not summaries_list:
                continue

            category_name = category.value if hasattr(category, "value") else str(category)

            total_files = sum(s.total_files for s in summaries_list)
            successful_files = sum(s.successful_files for s in summaries_list)
            success_rate = (successful_files / total_files * 100) if total_files > 0 else 0

            avg_speeds = [s.files_per_second for s in summaries_list if s.files_per_second]
            avg_speed = sum(avg_speeds) / len(avg_speeds) if avg_speeds else 0

            insights.append(
                f"### {category_name.title()} Category\n"
                f"- **Files processed**: {total_files:,}\n"
                f"- **Success rate**: {success_rate:.1f}%\n"
                f"- **Average speed**: {avg_speed:.2f} files/sec\n"
            )

        return "\n".join(insights) if insights else "No category data available."

    def _generate_interactive_pages(self, aggregated: AggregatedResults) -> None:
        """Generate interactive dashboard pages."""
        interactive_dir = self.results_dir / "interactive"
        interactive_dir.mkdir(exist_ok=True)

        dashboard_content = """---
title: Interactive Dashboard
description: Explore benchmark data interactively
---

# Interactive Dashboard

<iframe src="../assets/charts/interactive_dashboard.html"
        width="100%" height="800px" frameborder="0">
</iframe>

[Open Full Dashboard](../assets/charts/interactive_dashboard.html){ .md-button .md-button--primary target="_blank" }

## Raw Data Access

- [Aggregated Results JSON](../assets/data/aggregated_results.json)
- [Summary CSV](../assets/data/summary_results.csv)
- [Detailed Results CSV](../assets/data/detailed_results.csv)

"""

        with open(interactive_dir / "dashboard.md", "w") as f:
            f.write(dashboard_content)


def main() -> None:
    """CLI entry point for docs generation."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate MkDocs from benchmark results")
    parser.add_argument("--results-file", type=Path, required=True, help="Aggregated results JSON file")
    parser.add_argument("--charts-dir", type=Path, help="Directory containing chart files")
    parser.add_argument("--docs-dir", type=Path, default=Path("docs"), help="Documentation directory")

    args = parser.parse_args()

    generator = DocsGenerator(args.docs_dir)
    generator.generate_from_results(args.results_file, args.charts_dir)

    print(f"✅ Generated docs in {args.docs_dir}/results/")


if __name__ == "__main__":
    main()
