"""Generate comprehensive visualizations from benchmark results."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import msgspec
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
from plotly.subplots import make_subplots

from src.types import AggregatedResults

# Consistent color scheme for frameworks
FRAMEWORK_COLORS = {
    "kreuzberg_sync": "#2E86AB",  # Blue
    "kreuzberg_async": "#A23B72",  # Purple
    "docling": "#F18F01",  # Orange
    "markitdown": "#C73E1D",  # Red
    "unstructured": "#5B9A8B",  # Green
    "extractous": "#FF6B35",  # Orange-red (Rust color theme)
}


class BenchmarkVisualizer:
    """Generate comprehensive visualizations from benchmark results."""

    def __init__(self, output_dir: Path = Path("reports")) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set style for matplotlib/seaborn
        plt.style.use("default")

        # Set consistent color palette for frameworks
        framework_colors = list(FRAMEWORK_COLORS.values())
        sns.set_palette(framework_colors)

    def generate_all_visualizations(self, aggregated_file: Path) -> list[Path]:
        """Generate all visualizations from aggregated results."""
        # Load data
        with open(aggregated_file, "rb") as f:
            aggregated = msgspec.json.decode(f.read(), type=AggregatedResults)

        generated_files = []

        # Performance comparison charts
        generated_files.extend(self._generate_performance_charts(aggregated))

        # Success rate analysis
        generated_files.extend(self._generate_success_rate_charts(aggregated))

        # Memory and CPU usage charts
        generated_files.extend(self._generate_resource_charts(aggregated))

        # Data throughput charts
        generated_files.extend(self._generate_throughput_charts(aggregated))

        # Framework comparison heatmaps
        generated_files.extend(self._generate_heatmaps(aggregated))

        # Detailed category analysis
        generated_files.extend(self._generate_category_analysis(aggregated))

        # Format breakdown analysis
        generated_files.extend(self._generate_format_breakdown(aggregated))

        # Interactive dashboard
        generated_files.extend(self._generate_interactive_dashboard(aggregated))

        # Quality assessment charts (if quality data available)
        generated_files.extend(self._generate_quality_charts(aggregated))

        return generated_files

    def _generate_performance_charts(self, aggregated: AggregatedResults) -> list[Path]:
        """Generate performance comparison charts."""
        files = []

        # Prepare data for plotting
        perf_data = [
            {
                "Framework": framework.value,
                "Category": summary.category.value,
                "Avg Time (s)": summary.avg_extraction_time,
                "Median Time (s)": summary.median_extraction_time or 0,
                "Success Rate (%)": summary.success_rate * 100,
                "Files per Second": summary.files_per_second or 0,
                "Total Files": summary.total_files,
            }
            for framework, summaries in aggregated.framework_summaries.items()
            for summary in summaries
            if summary.avg_extraction_time is not None
        ]

        if not perf_data:
            return files

        df = pd.DataFrame(perf_data)

        # 1. Performance comparison bar chart
        fig = plt.figure(figsize=(12, 8))
        df_pivot = df.pivot(index="Framework", columns="Category", values="Avg Time (s)")

        # Use consistent colors for frameworks
        colors = [FRAMEWORK_COLORS.get(fw, "#999999") for fw in df_pivot.index]
        ax = df_pivot.plot(kind="bar", ax=plt.gca(), color=colors)
        plt.title("Average Extraction Time by Framework and Category", fontsize=16, fontweight="bold")
        plt.ylabel("Time (seconds)", fontsize=12)
        plt.xlabel("Framework", fontsize=12)
        plt.xticks(rotation=45)
        plt.legend(title="Document Category", title_fontsize=12)
        plt.grid(axis="y", alpha=0.3)
        plt.tight_layout()

        perf_chart = self.output_dir / "performance_comparison.png"
        plt.savefig(perf_chart, dpi=300, bbox_inches="tight")
        plt.close()
        files.append(perf_chart)

        # 2. Throughput comparison
        fig = plt.figure(figsize=(12, 8))
        df_pivot = df.pivot(index="Framework", columns="Category", values="Files per Second")

        # Use consistent colors for frameworks
        colors = [FRAMEWORK_COLORS.get(fw, "#999999") for fw in df_pivot.index]
        ax = df_pivot.plot(kind="bar", ax=plt.gca(), color=colors)
        plt.title("Throughput Comparison by Framework and Category", fontsize=16, fontweight="bold")
        plt.ylabel("Files per Second", fontsize=12)
        plt.xlabel("Framework", fontsize=12)
        plt.xticks(rotation=45)
        plt.legend(title="Document Category", title_fontsize=12)
        plt.grid(axis="y", alpha=0.3)
        plt.tight_layout()

        throughput_chart = self.output_dir / "throughput_comparison.png"
        plt.savefig(throughput_chart, dpi=300, bbox_inches="tight")
        plt.close()
        files.append(throughput_chart)

        return files

    def _generate_success_rate_charts(self, aggregated: AggregatedResults) -> list[Path]:
        """Generate success rate analysis charts."""
        files = []

        # Determine expected files per category from the data
        expected_files_per_category = {}
        for category, cat_summaries in aggregated.category_summaries.items():
            # Get the maximum files tested in each category
            max_files = max(s.total_files for s in cat_summaries)
            expected_files_per_category[category] = max_files

        # Total expected files across all categories
        total_expected_files = sum(expected_files_per_category.values())

        # Prepare success rate data
        success_data = []
        for framework, summaries in aggregated.framework_summaries.items():
            success_files = sum(s.successful_files for s in summaries)
            total_files = sum(s.total_files for s in summaries)
            failed_files = sum(s.failed_files for s in summaries)
            timeout_files = sum(s.timeout_files for s in summaries)

            # Calculate success rate based on files actually tested
            success_rate = (success_files / total_files * 100) if total_files > 0 else 0

            success_data.append(
                {
                    "Framework": framework.value,
                    "Success Rate (%)": success_rate,
                    "Total Files": total_files,
                    "Successful": success_files,
                    "Failed": failed_files,
                    "Timeout": timeout_files,
                    "Tested": total_files,
                }
            )

        if not success_data:
            return files

        df = pd.DataFrame(success_data)

        # Success rate comparison
        fig = plt.figure(figsize=(12, 7))
        bars = plt.bar(df["Framework"], df["Success Rate (%)"])
        plt.title("Success Rate by Framework (All Categories)", fontsize=14, fontweight="bold")
        plt.ylabel("Success Rate (%)")
        plt.xlabel("Framework")
        plt.xticks(rotation=45)
        plt.ylim(0, 105)

        # Add detailed value labels on bars
        for _i, (bar, row) in enumerate(zip(bars, df.itertuples(), strict=False)):
            height = bar.get_height()
            # Show success rate and breakdown
            # Access by index since itertuples creates a namedtuple
            total_files = row[3]  # Total Files column
            successful = row[4]  # Successful column
            failed = row[5]  # Failed column
            timeout = row[6]  # Timeout column

            if failed > 0 or timeout > 0:
                label = f"{height:.1f}%\n({successful}/{total_files})"
                if timeout > 0:
                    label += f"\nTimeout: {timeout}"
                color = "red" if height < 90 else "black"
            else:
                label = f"{height:.1f}%\n({successful}/{total_files})"
                color = "black"
            plt.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 1,
                label,
                ha="center",
                va="bottom",
                fontsize=9,
                color=color,
            )

        # Add note about calculation method
        plt.text(
            0.02,
            0.98,
            "Success rate calculated on files actually tested by each framework\nFrameworks tested different numbers of files based on their capabilities\nKreuzberg (both): tiny, small, medium categories\nDocling/MarkItDown: tiny, small categories only\nUnstructured/Extractous: tiny, small, medium categories",
            transform=plt.gca().transAxes,
            fontsize=9,
            verticalalignment="top",
            bbox={"boxstyle": "round", "facecolor": "lightyellow", "alpha": 0.8},
        )

        plt.tight_layout()
        success_chart = self.output_dir / "success_rate_comparison.png"
        plt.savefig(success_chart, dpi=300, bbox_inches="tight")
        plt.close()
        files.append(success_chart)

        return files

    def _generate_resource_charts(self, aggregated: AggregatedResults) -> list[Path]:
        """Generate memory and CPU usage charts."""
        files = []

        # Memory usage data
        memory_data = [
            {
                "Framework": framework.value,
                "Category": summary.category.value,
                "Peak Memory (MB)": summary.avg_peak_memory_mb or 0,
                "Avg CPU (%)": summary.avg_cpu_percent or 0,
            }
            for framework, summaries in aggregated.framework_summaries.items()
            for summary in summaries
            if summary.avg_peak_memory_mb is not None
        ]

        if memory_data:
            df_memory = pd.DataFrame(memory_data)

            # Check if we have meaningful memory data (not all zeros)
            has_memory_data = df_memory["Peak Memory (MB)"].sum() > 0

            if has_memory_data:
                # Create memory usage chart
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

                # Memory usage by framework and category
                df_pivot = df_memory.pivot(index="Framework", columns="Category", values="Peak Memory (MB)")
                colors = [FRAMEWORK_COLORS.get(fw, "#999999") for fw in df_pivot.index]
                df_pivot.plot(kind="bar", ax=ax1, color=colors)
                ax1.set_title("Peak Memory Usage by Framework and Category", fontsize=14, fontweight="bold")
                ax1.set_ylabel("Peak Memory (MB)", fontsize=12)
                ax1.set_xlabel("Framework", fontsize=12)
                ax1.tick_params(axis="x", rotation=45)
                ax1.legend(title="Document Category", title_fontsize=10)
                ax1.grid(axis="y", alpha=0.3)

                # CPU usage chart
                df_pivot_cpu = df_memory.pivot(index="Framework", columns="Category", values="Avg CPU (%)")
                df_pivot_cpu.plot(kind="bar", ax=ax2, color=colors)
                ax2.set_title("Average CPU Usage by Framework and Category", fontsize=14, fontweight="bold")
                ax2.set_ylabel("Average CPU (%)", fontsize=12)
                ax2.set_xlabel("Framework", fontsize=12)
                ax2.tick_params(axis="x", rotation=45)
                ax2.legend(title="Document Category", title_fontsize=10)
                ax2.grid(axis="y", alpha=0.3)

                plt.tight_layout()
                memory_chart = self.output_dir / "memory_usage.png"
                plt.savefig(memory_chart, dpi=300, bbox_inches="tight")
                plt.close()
                files.append(memory_chart)
            else:
                # Create placeholder chart indicating no memory data
                fig = plt.figure(figsize=(12, 8))
                plt.text(
                    0.5,
                    0.5,
                    "Memory profiling data not available\n(All values are 0.0)",
                    fontsize=16,
                    ha="center",
                    va="center",
                    transform=plt.gca().transAxes,
                    bbox={"boxstyle": "round,pad=0.5", "facecolor": "lightgray"},
                )
                plt.title("Memory Usage Analysis", fontsize=16, fontweight="bold")
                plt.axis("off")
                memory_chart = self.output_dir / "memory_usage.png"
                plt.savefig(memory_chart, dpi=300, bbox_inches="tight")
                plt.close()
                files.append(memory_chart)

        return files

    def _generate_throughput_charts(self, aggregated: AggregatedResults) -> list[Path]:
        """Generate data throughput charts."""
        files = []

        # Data throughput chart
        throughput_data = [
            {
                "Framework": framework.value,
                "Category": summary.category.value,
                "Throughput (MB/s)": summary.mb_per_second or 0,
            }
            for framework, summaries in aggregated.framework_summaries.items()
            for summary in summaries
            if summary.mb_per_second is not None
        ]

        if throughput_data:
            df_throughput = pd.DataFrame(throughput_data)
            fig = plt.figure(figsize=(12, 8))
            df_pivot = df_throughput.pivot(index="Framework", columns="Category", values="Throughput (MB/s)")

            # Use consistent colors
            colors = [FRAMEWORK_COLORS.get(fw, "#999999") for fw in df_pivot.index]
            ax = df_pivot.plot(kind="bar", ax=plt.gca(), color=colors)
            plt.title("Data Throughput by Framework and Category", fontsize=16, fontweight="bold")
            plt.ylabel("Throughput (MB/s)", fontsize=12)
            plt.xlabel("Framework", fontsize=12)
            plt.xticks(rotation=45)
            plt.legend(title="Document Category", title_fontsize=12)
            plt.grid(axis="y", alpha=0.3)
            plt.tight_layout()

            throughput_chart = self.output_dir / "data_throughput.png"
            plt.savefig(throughput_chart, dpi=300, bbox_inches="tight")
            plt.close()
            files.append(throughput_chart)

        return files

    def _generate_heatmaps(self, aggregated: AggregatedResults) -> list[Path]:
        """Generate framework vs category heatmaps."""
        files = []

        # Create matrices for different metrics
        frameworks = list(aggregated.framework_summaries.keys())
        categories = set()
        for summaries in aggregated.framework_summaries.values():
            categories.update(s.category for s in summaries)
        categories = sorted(categories, key=lambda x: x.value)

        if not frameworks or not categories:
            return files

        # Performance heatmap
        perf_matrix = []
        for framework in frameworks:
            row = []
            summaries = {s.category: s for s in aggregated.framework_summaries[framework]}
            for category in categories:
                if category in summaries and summaries[category].avg_extraction_time:
                    row.append(summaries[category].avg_extraction_time)
                else:
                    row.append(0)
            perf_matrix.append(row)

        if any(any(row) for row in perf_matrix):
            fig = plt.figure(figsize=(10, 8))
            sns.heatmap(
                perf_matrix,
                xticklabels=[c.value for c in categories],
                yticklabels=[f.value for f in frameworks],
                annot=True,
                fmt=".2f",
                cmap="YlOrRd",
            )
            plt.title("Average Extraction Time Heatmap (seconds)")
            plt.xlabel("Document Category")
            plt.ylabel("Framework")
            plt.tight_layout()

            heatmap_file = self.output_dir / "performance_heatmap.png"
            plt.savefig(heatmap_file, dpi=300, bbox_inches="tight")
            plt.close()
            files.append(heatmap_file)

        return files

    def _generate_category_analysis(self, aggregated: AggregatedResults) -> list[Path]:
        """Generate detailed category analysis."""
        files = []

        # Category performance breakdown
        category_data = [
            {
                "Category": category.value,
                "Framework": summary.framework.value,
                "Avg Time (s)": summary.avg_extraction_time,
                "Success Rate (%)": summary.success_rate * 100,
                "Total Files": summary.total_files,
            }
            for category, summaries in aggregated.category_summaries.items()
            for summary in summaries
            if summary.avg_extraction_time is not None
        ]

        if not category_data:
            return files

        df = pd.DataFrame(category_data)

        # Category analysis by framework
        fig = plt.figure(figsize=(14, 8))

        # Group by category and framework for proper visualization
        df_grouped = df.groupby(["Category", "Framework"])["Avg Time (s)"].mean().unstack()

        # Use consistent colors for frameworks
        framework_colors = [FRAMEWORK_COLORS.get(fw, "#999999") for fw in df_grouped.columns]
        ax = df_grouped.plot(kind="bar", ax=plt.gca(), color=framework_colors, width=0.8)

        plt.title("Average Processing Time by Category and Framework", fontsize=16, fontweight="bold")
        plt.ylabel("Average Time (seconds)", fontsize=12)
        plt.xlabel("Document Category", fontsize=12)
        plt.xticks(rotation=45)
        plt.legend(title="Framework", title_fontsize=12, bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.grid(axis="y", alpha=0.3)
        plt.tight_layout()

        category_chart = self.output_dir / "category_analysis.png"
        plt.savefig(category_chart, dpi=300, bbox_inches="tight")
        plt.close()
        files.append(category_chart)

        return files

    def _generate_interactive_dashboard(self, aggregated: AggregatedResults) -> list[Path]:
        """Generate interactive Plotly dashboard."""
        files = []

        # Prepare comprehensive data
        all_data = [
            {
                "Framework": framework.value,
                "Category": summary.category.value,
                "Avg Time (s)": summary.avg_extraction_time or 0,
                "Success Rate (%)": summary.success_rate * 100,
                "Peak Memory (MB)": summary.avg_peak_memory_mb or 0,
                "CPU Usage (%)": summary.avg_cpu_percent or 0,
                "Files per Second": summary.files_per_second or 0,
                "Total Files": summary.total_files,
                "Successful Files": summary.successful_files,
                "Failed Files": summary.failed_files,
            }
            for framework, summaries in aggregated.framework_summaries.items()
            for summary in summaries
        ]

        if not all_data:
            return files

        df = pd.DataFrame(all_data)

        # Create interactive dashboard
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=("Performance Comparison", "Success Rates", "Resource Usage", "Throughput Analysis"),
            specs=[[{"secondary_y": False}, {"secondary_y": False}], [{"secondary_y": False}, {"secondary_y": False}]],
        )

        # Performance comparison
        for framework in df["Framework"].unique():
            fw_data = df[df["Framework"] == framework]
            fig.add_trace(
                go.Bar(
                    x=fw_data["Category"], y=fw_data["Avg Time (s)"], name=f"{framework} (Time)", legendgroup=framework
                ),
                row=1,
                col=1,
            )

        # Success rates
        for framework in df["Framework"].unique():
            fw_data = df[df["Framework"] == framework]
            fig.add_trace(
                go.Bar(
                    x=fw_data["Category"],
                    y=fw_data["Success Rate (%)"],
                    name=f"{framework} (Success)",
                    legendgroup=framework,
                    showlegend=False,
                ),
                row=1,
                col=2,
            )

        # Memory usage
        fig.add_trace(
            go.Scatter(
                x=df["Framework"],
                y=df["Peak Memory (MB)"],
                mode="markers",
                marker={"size": df["Total Files"], "sizemode": "diameter", "sizeref": 2},
                name="Memory Usage",
                showlegend=False,
            ),
            row=2,
            col=1,
        )

        # Throughput
        for framework in df["Framework"].unique():
            fw_data = df[df["Framework"] == framework]
            fig.add_trace(
                go.Scatter(
                    x=fw_data["Category"],
                    y=fw_data["Files per Second"],
                    mode="lines+markers",
                    name=f"{framework} (Throughput)",
                    legendgroup=framework,
                    showlegend=False,
                ),
                row=2,
                col=2,
            )

        fig.update_layout(height=800, title_text="Comprehensive Benchmark Dashboard", showlegend=True)

        # Save interactive HTML
        dashboard_file = self.output_dir / "interactive_dashboard.html"
        fig.write_html(dashboard_file)
        files.append(dashboard_file)

        return files

    def _generate_quality_charts(self, aggregated: AggregatedResults) -> list[Path]:
        """Generate quality assessment visualizations."""
        files = []

        # Check if we have quality data
        quality_data = []
        has_quality_data = False

        # This would need to be updated to use quality-enhanced results
        # For now, return empty to avoid breaking existing functionality

        return files

    def generate_summary_metrics(self, aggregated_file: Path) -> dict[str, Any]:
        """Generate summary metrics for README."""
        with open(aggregated_file, "rb") as f:
            aggregated = msgspec.json.decode(f.read(), type=AggregatedResults)

        # Calculate key metrics
        total_files = aggregated.total_files_processed
        total_time = aggregated.total_time_seconds
        frameworks_tested = len(aggregated.framework_summaries)
        categories_tested = len(aggregated.category_summaries)

        # Find best performing framework
        best_framework = None
        best_avg_time = float("inf")

        # Determine expected files per category from the data
        expected_files_per_category = {}
        for category, cat_summaries in aggregated.category_summaries.items():
            max_files = max(s.total_files for s in cat_summaries)
            expected_files_per_category[category] = max_files

        total_expected_files = sum(expected_files_per_category.values())

        framework_stats = {}
        for framework, summaries in aggregated.framework_summaries.items():
            success_fw_files = sum(s.successful_files for s in summaries)

            # Check which categories this framework tested
            tested_categories = {s.category for s in summaries}
            all_categories = set(expected_files_per_category.keys())
            missing_categories = all_categories - tested_categories
            missing_files = sum(expected_files_per_category[cat] for cat in missing_categories)

            # Calculate fair success rate using all expected files
            success_rate = (success_fw_files / total_expected_files * 100) if total_expected_files > 0 else 0

            # Calculate average time across all categories
            times = [s.avg_extraction_time for s in summaries if s.avg_extraction_time is not None]
            avg_time = sum(times) / len(times) if times else float("inf")

            framework_stats[framework.value] = {
                "success_rate": success_rate,
                "avg_time": avg_time,
                "total_files": sum(s.total_files for s in summaries),
                "successful_files": success_fw_files,
                "expected_files": total_expected_files,
                "missing_files": missing_files,
            }

            if avg_time < best_avg_time and success_rate > 80:  # Only consider frameworks with good success rate
                best_avg_time = avg_time
                best_framework = framework.value

        return {
            "total_files": total_files,
            "total_time": total_time,
            "frameworks_tested": frameworks_tested,
            "categories_tested": categories_tested,
            "best_framework": best_framework,
            "framework_stats": framework_stats,
            "timestamp": aggregated_file.stat().st_mtime,
        }

    def generate_installation_size_chart(self, installation_sizes_file: Path) -> Path:
        """Generate installation size comparison chart."""
        import json

        # Load installation size data
        with open(installation_sizes_file) as f:
            size_data = json.load(f)

        # Filter out failed installations
        successful_data = {name: data for name, data in size_data.items() if "error" not in data}

        if not successful_data:
            raise ValueError("No successful installation size data available")

        # Create DataFrame
        df_data = []
        for framework, data in successful_data.items():
            df_data.append(
                {
                    "Framework": framework.replace("_", " ").title(),
                    "Size (MB)": data["size_mb"],
                    "Dependencies": data["package_count"],
                    "Description": data["description"],
                }
            )

        df = pd.DataFrame(df_data)
        df = df.sort_values("Size (MB)")

        # Create visualization with 3 subplots
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(24, 8))

        # Size comparison bar chart
        colors = [FRAMEWORK_COLORS.get(fw.lower().replace(" ", "_"), "#1f77b4") for fw in df["Framework"]]

        bars1 = ax1.bar(df["Framework"], df["Size (MB)"], color=colors, alpha=0.8)
        ax1.set_title("Installation Size Comparison", fontsize=16, fontweight="bold")
        ax1.set_xlabel("Framework", fontsize=12)
        ax1.set_ylabel("Installation Size (MB)", fontsize=12)
        ax1.tick_params(axis="x", rotation=45)

        # Add value labels on bars
        for bar, value in zip(bars1, df["Size (MB)"], strict=False):
            height = bar.get_height()
            ax1.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + height * 0.01,
                f"{value:.1f} MB",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        # Dependencies comparison
        bars2 = ax2.bar(df["Framework"], df["Dependencies"], color=colors, alpha=0.8)
        ax2.set_title("Dependency Count Comparison", fontsize=16, fontweight="bold")
        ax2.set_xlabel("Framework", fontsize=12)
        ax2.set_ylabel("Number of Dependencies", fontsize=12)
        ax2.tick_params(axis="x", rotation=45)

        # Add value labels on bars
        for bar, value in zip(bars2, df["Dependencies"], strict=False):
            height = bar.get_height()
            ax2.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + height * 0.01,
                f"{value}",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        # Memory efficiency (Storage per dependency)
        df["MB per Dependency"] = df["Size (MB)"] / df["Dependencies"]
        bars3 = ax3.bar(df["Framework"], df["MB per Dependency"], color=colors, alpha=0.8)
        ax3.set_title("Storage Efficiency\n(MB per Dependency)", fontsize=16, fontweight="bold")
        ax3.set_xlabel("Framework", fontsize=12)
        ax3.set_ylabel("MB per Dependency", fontsize=12)
        ax3.tick_params(axis="x", rotation=45)

        # Add value labels on bars
        for bar, value in zip(bars3, df["MB per Dependency"], strict=False):
            height = bar.get_height()
            ax3.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + height * 0.01,
                f"{value:.2f}",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        plt.tight_layout()

        # Save chart
        output_file = self.output_dir / "installation_sizes.png"
        plt.savefig(output_file, dpi=300, bbox_inches="tight")
        plt.close()

        return output_file

    def _generate_format_breakdown(self, aggregated: AggregatedResults) -> list[Path]:
        """Generate format breakdown visualization showing success by file type."""
        files = []

        # Collect data by file type across frameworks
        format_data = {}

        # Get all file types from the data
        all_file_types = set()
        for fw_summaries in aggregated.framework_summaries.values():
            for summary in fw_summaries:
                # Extract file type data from detailed results if available
                all_file_types.add(summary.category.value)

        # For now, let's create a placeholder that shows format support
        # We'll need to enhance this with actual per-format results
        from .config import FRAMEWORK_EXCLUSIONS

        # Create format support matrix
        formats = [
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
        ]

        frameworks = ["kreuzberg_sync", "docling", "markitdown", "unstructured", "extractous"]

        # Create support matrix
        support_matrix = []
        for fw in frameworks:
            fw_support = []
            exclusions = FRAMEWORK_EXCLUSIONS.get(fw, set())
            for fmt in formats:
                if fmt in exclusions:
                    fw_support.append(0)  # Not supported
                else:
                    fw_support.append(1)  # Supported
            support_matrix.append(fw_support)

        # Create heatmap
        fig, ax = plt.subplots(figsize=(14, 8))

        # Create the heatmap
        im = ax.imshow(support_matrix, cmap="RdYlGn", aspect="auto", vmin=0, vmax=1)

        # Set ticks and labels
        ax.set_xticks(range(len(formats)))
        ax.set_yticks(range(len(frameworks)))
        ax.set_xticklabels(formats, rotation=45, ha="right")
        ax.set_yticklabels([fw.replace("_", " ").title() for fw in frameworks])

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label("Format Support", rotation=270, labelpad=20)
        cbar.set_ticks([0, 1])
        cbar.set_ticklabels(["Not Supported", "Supported"])

        # Add text annotations
        for i in range(len(frameworks)):
            for j in range(len(formats)):
                text = ax.text(
                    j,
                    i,
                    "✓" if support_matrix[i][j] else "✗",
                    ha="center",
                    va="center",
                    color="white" if support_matrix[i][j] else "black",
                    fontsize=10,
                    fontweight="bold",
                )

        plt.title("File Format Support Matrix by Framework", fontsize=16, fontweight="bold", pad=20)
        plt.tight_layout()

        # Save chart
        output_file = self.output_dir / "format_support_matrix.png"
        plt.savefig(output_file, dpi=300, bbox_inches="tight")
        plt.close()

        files.append(output_file)
        return files
