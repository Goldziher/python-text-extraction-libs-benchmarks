"""Reporting and visualization utilities for benchmark results."""

from __future__ import annotations

import sys
from pathlib import Path

if sys.version_info >= (3, 13):
    pass
else:
    pass

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from rich.console import Console
from rich.table import Table

from .types import BenchmarkResult, BenchmarkSummary

console = Console()


class BenchmarkReporter:
    """Generate reports and visualizations from benchmark results."""

    def __init__(self, results: list[BenchmarkResult], summaries: list[BenchmarkSummary]) -> None:
        """Initialize reporter with results and summaries.

        Args:
            results: List of individual benchmark results.
            summaries: List of benchmark summaries.
        """
        self.results = results
        self.summaries = summaries

    def print_summary_table(self) -> None:
        """Print a summary table to the console."""
        table = Table(title="Benchmark Results Summary")

        table.add_column("Framework", style="cyan", no_wrap=True)
        table.add_column("File Type", style="magenta")
        table.add_column("Total Files", justify="right")
        table.add_column("Success Rate", justify="right")
        table.add_column("Avg Time (s)", justify="right")
        table.add_column("Avg Memory (MB)", justify="right")
        table.add_column("Avg CPU (%)", justify="right")

        for summary in self.summaries:
            success_rate = (
                f"{summary.successful_extractions / summary.total_files * 100:.1f}%"
                if summary.total_files > 0
                else "0.0%"
            )

            table.add_row(
                summary.framework.value,
                summary.file_type.value,
                str(summary.total_files),
                success_rate,
                f"{summary.average_time_seconds:.2f}",
                f"{summary.average_memory_mb:.1f}",
                f"{summary.average_cpu_percent:.1f}",
            )

        console.print(table)

        # Print format support information
        self._print_format_support_info()

    def _print_format_support_info(self) -> None:
        """Print format support information."""
        from .config import FRAMEWORK_EXCLUSIONS

        console.print("\n[bold cyan]Format Support Information[/bold cyan]")
        console.print("Testing ALL 18 formats. Frameworks skip unsupported formats:\n")

        # Create format support table
        support_table = Table(title="Framework Format Exclusions")
        support_table.add_column("Framework", style="cyan", no_wrap=True)
        support_table.add_column("Excluded Formats", style="red")
        support_table.add_column("Supported", style="green", justify="right")

        all_formats = {
            ".pdf",
            ".docx",
            ".pptx",
            ".xlsx",
            ".xls",
            ".html",
            ".md",
            ".txt",
            ".csv",
            ".json",
            ".yaml",
            ".png",
            ".jpg",
            ".jpeg",
            ".bmp",
            ".eml",
            ".msg",
            ".odt",
            ".rst",
            ".org",
        }

        for framework, exclusions in FRAMEWORK_EXCLUSIONS.items():
            if framework in [
                "kreuzberg_sync",
                "docling",
                "markitdown",
                "unstructured",
                "extractous",
                "pymupdf",
                "pdfplumber",
            ]:
                excluded = ", ".join(sorted(exclusions))
                supported_count = len(all_formats - exclusions)
                support_table.add_row(
                    framework.replace("_", " ").title(), excluded if excluded else "None", f"{supported_count}/20"
                )

        console.print(support_table)

    def save_results_csv(self, output_path: str | Path) -> None:
        """Save detailed results to CSV file.

        Args:
            output_path: Path to save the CSV file.
        """
        df = pd.DataFrame(
            [
                {
                    "framework": result.framework.value,
                    "file_type": result.file_type.value,
                    "file_path": result.file_path,
                    "file_size_bytes": result.file_size_bytes,
                    "extraction_time_seconds": result.extraction_time_seconds,
                    "memory_peak_mb": result.memory_peak_mb,
                    "cpu_percent": result.cpu_percent,
                    "success": result.success,
                    "error_message": result.error_message,
                    "extracted_text_length": result.extracted_text_length,
                }
                for result in self.results
            ]
        )

        df.to_csv(output_path, index=False)
        console.print(f"Results saved to: {output_path}")

    def save_summary_csv(self, output_path: str | Path) -> None:
        """Save summary statistics to CSV file.

        Args:
            output_path: Path to save the CSV file.
        """
        df = pd.DataFrame(
            [
                {
                    "framework": summary.framework.value,
                    "file_type": summary.file_type.value,
                    "total_files": summary.total_files,
                    "successful_extractions": summary.successful_extractions,
                    "failed_extractions": summary.failed_extractions,
                    "success_rate": summary.successful_extractions / summary.total_files
                    if summary.total_files > 0
                    else 0.0,
                    "average_time_seconds": summary.average_time_seconds,
                    "median_time_seconds": summary.median_time_seconds,
                    "min_time_seconds": summary.min_time_seconds,
                    "max_time_seconds": summary.max_time_seconds,
                    "average_memory_mb": summary.average_memory_mb,
                    "average_cpu_percent": summary.average_cpu_percent,
                    "total_time_seconds": summary.total_time_seconds,
                }
                for summary in self.summaries
            ]
        )

        df.to_csv(output_path, index=False)
        console.print(f"Summary saved to: {output_path}")

    def create_performance_charts(self, output_dir: str | Path) -> None:
        """Create performance visualization charts.

        Args:
            output_dir: Directory to save chart files.
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Set up matplotlib style
        plt.style.use("seaborn-v0_8")
        sns.set_palette("husl")

        # Create DataFrame from summaries for easier plotting
        df = pd.DataFrame(
            [
                {
                    "framework": summary.framework.value,
                    "file_type": summary.file_type.value,
                    "average_time_seconds": summary.average_time_seconds,
                    "average_memory_mb": summary.average_memory_mb,
                    "average_cpu_percent": summary.average_cpu_percent,
                    "success_rate": summary.successful_extractions / summary.total_files
                    if summary.total_files > 0
                    else 0.0,
                }
                for summary in self.summaries
                if summary.successful_extractions > 0  # Only include successful runs
            ]
        )

        if df.empty:
            console.print("No successful results to plot")
            return

        # 1. Performance Time Comparison
        self._create_time_comparison_chart(df, output_path)

        # 2. Memory Usage Comparison
        self._create_memory_comparison_chart(df, output_path)

        # 3. Success Rate Comparison
        self._create_success_rate_chart(df, output_path)

        # 4. Overall Performance Heatmap
        self._create_performance_heatmap(df, output_path)

        console.print(f"Charts saved to: {output_path}")

    def _create_time_comparison_chart(self, df: pd.DataFrame, output_path: Path) -> None:
        """Create extraction time comparison chart."""
        plt.figure(figsize=(12, 8))
        pivot_df = df.pivot(index="file_type", columns="framework", values="average_time_seconds")

        ax = pivot_df.plot(kind="bar", figsize=(12, 8))
        plt.title("Average Extraction Time by Framework and File Type")
        plt.xlabel("File Type")
        plt.ylabel("Average Time (seconds)")
        plt.xticks(rotation=45)
        plt.legend(title="Framework", bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.tight_layout()

        plt.savefig(output_path / "extraction_time_comparison.png", dpi=300, bbox_inches="tight")
        plt.close()

    def _create_memory_comparison_chart(self, df: pd.DataFrame, output_path: Path) -> None:
        """Create memory usage comparison chart."""
        plt.figure(figsize=(12, 8))
        pivot_df = df.pivot(index="file_type", columns="framework", values="average_memory_mb")

        ax = pivot_df.plot(kind="bar", figsize=(12, 8))
        plt.title("Average Memory Usage by Framework and File Type")
        plt.xlabel("File Type")
        plt.ylabel("Average Memory (MB)")
        plt.xticks(rotation=45)
        plt.legend(title="Framework", bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.tight_layout()

        plt.savefig(output_path / "memory_usage_comparison.png", dpi=300, bbox_inches="tight")
        plt.close()

    def _create_success_rate_chart(self, df: pd.DataFrame, output_path: Path) -> None:
        """Create success rate comparison chart."""
        # Calculate success rates from original summaries
        success_data = []
        for summary in self.summaries:
            success_rate = summary.successful_extractions / summary.total_files if summary.total_files > 0 else 0.0
            success_data.append(
                {
                    "framework": summary.framework.value,
                    "file_type": summary.file_type.value,
                    "success_rate": success_rate,
                }
            )

        success_df = pd.DataFrame(success_data)
        pivot_df = success_df.pivot(index="file_type", columns="framework", values="success_rate")

        plt.figure(figsize=(12, 8))
        ax = pivot_df.plot(kind="bar", figsize=(12, 8))
        plt.title("Success Rate by Framework and File Type")
        plt.xlabel("File Type")
        plt.ylabel("Success Rate")
        plt.xticks(rotation=45)
        plt.ylim(0, 1.05)
        plt.legend(title="Framework", bbox_to_anchor=(1.05, 1), loc="upper left")

        # Format y-axis as percentage
        from matplotlib.ticker import FuncFormatter

        ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:.0%}"))

        plt.tight_layout()
        plt.savefig(output_path / "success_rate_comparison.png", dpi=300, bbox_inches="tight")
        plt.close()

    def _create_performance_heatmap(self, df: pd.DataFrame, output_path: Path) -> None:
        """Create performance heatmap."""
        # Normalize metrics to 0-1 scale for comparison
        metrics_df = df.copy()

        # Lower time is better, so invert
        if not metrics_df.empty and metrics_df["average_time_seconds"].max() > 0:
            metrics_df["time_score"] = 1 - (
                metrics_df["average_time_seconds"] / metrics_df["average_time_seconds"].max()
            )
        else:
            metrics_df["time_score"] = 0

        # Lower memory is better, so invert
        if not metrics_df.empty and metrics_df["average_memory_mb"].max() > 0:
            metrics_df["memory_score"] = 1 - (metrics_df["average_memory_mb"] / metrics_df["average_memory_mb"].max())
        else:
            metrics_df["memory_score"] = 0

        # Success rate is already 0-1
        metrics_df["success_score"] = metrics_df["success_rate"]

        # Calculate overall performance score
        metrics_df["overall_score"] = (
            metrics_df["time_score"] * 0.4 + metrics_df["memory_score"] * 0.3 + metrics_df["success_score"] * 0.3
        )

        # Create heatmap
        heatmap_data = metrics_df.pivot(index="file_type", columns="framework", values="overall_score")

        plt.figure(figsize=(12, 8))
        sns.heatmap(
            heatmap_data,
            annot=True,
            fmt=".2f",
            cmap="RdYlGn",
            center=0.5,
            cbar_kws={"label": "Performance Score (Higher is Better)"},
        )
        plt.title("Overall Performance Heatmap\n(Weighted: Time 40%, Memory 30%, Success Rate 30%)")
        plt.xlabel("Framework")
        plt.ylabel("File Type")
        plt.tight_layout()

        plt.savefig(output_path / "performance_heatmap.png", dpi=300, bbox_inches="tight")
        plt.close()
