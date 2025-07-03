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


class BenchmarkVisualizer:
    """Generate comprehensive visualizations from benchmark results."""

    def __init__(self, output_dir: Path = Path("reports")) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set style for matplotlib/seaborn
        plt.style.use("default")
        sns.set_palette("husl")

    def generate_all_visualizations(self, aggregated_file: Path) -> list[Path]:
        """Generate all visualizations from aggregated results."""
        # Load data
        with open(aggregated_file, "rb") as f:
            data = msgspec.json.decode(f.read())

        aggregated = AggregatedResults(**data) if isinstance(data, dict) else data

        generated_files = []

        # Performance comparison charts
        generated_files.extend(self._generate_performance_charts(aggregated))

        # Success rate analysis
        generated_files.extend(self._generate_success_rate_charts(aggregated))

        # Resource utilization charts
        generated_files.extend(self._generate_resource_charts(aggregated))

        # Framework comparison heatmaps
        generated_files.extend(self._generate_heatmaps(aggregated))

        # Detailed category analysis
        generated_files.extend(self._generate_category_analysis(aggregated))

        # Interactive dashboard
        generated_files.extend(self._generate_interactive_dashboard(aggregated))

        return generated_files

    def _generate_performance_charts(self, aggregated: AggregatedResults) -> list[Path]:
        """Generate performance comparison charts."""
        files = []

        # Prepare data for plotting
        perf_data = []
        for framework, summaries in aggregated.framework_summaries.items():
            for summary in summaries:
                if summary.avg_extraction_time is not None:
                    perf_data.append(
                        {
                            "Framework": framework.value,
                            "Category": summary.category.value,
                            "Avg Time (s)": summary.avg_extraction_time,
                            "Median Time (s)": summary.median_extraction_time or 0,
                            "Success Rate (%)": summary.success_rate * 100,
                            "Files per Second": summary.files_per_second or 0,
                            "Total Files": summary.total_files,
                        }
                    )

        if not perf_data:
            return files

        df = pd.DataFrame(perf_data)

        # 1. Performance comparison bar chart
        fig = plt.figure(figsize=(12, 8))
        df_pivot = df.pivot(index="Framework", columns="Category", values="Avg Time (s)")
        ax = df_pivot.plot(kind="bar", ax=plt.gca())
        plt.title("Average Extraction Time by Framework and Category")
        plt.ylabel("Time (seconds)")
        plt.xlabel("Framework")
        plt.xticks(rotation=45)
        plt.legend(title="Document Category")
        plt.tight_layout()

        perf_chart = self.output_dir / "performance_comparison.png"
        plt.savefig(perf_chart, dpi=300, bbox_inches="tight")
        plt.close()
        files.append(perf_chart)

        # 2. Throughput comparison
        fig = plt.figure(figsize=(12, 8))
        df_pivot = df.pivot(index="Framework", columns="Category", values="Files per Second")
        ax = df_pivot.plot(kind="bar", ax=plt.gca())
        plt.title("Throughput by Framework and Category")
        plt.ylabel("Files per Second")
        plt.xlabel("Framework")
        plt.xticks(rotation=45)
        plt.legend(title="Document Category")
        plt.tight_layout()

        throughput_chart = self.output_dir / "throughput_comparison.png"
        plt.savefig(throughput_chart, dpi=300, bbox_inches="tight")
        plt.close()
        files.append(throughput_chart)

        return files

    def _generate_success_rate_charts(self, aggregated: AggregatedResults) -> list[Path]:
        """Generate success rate analysis charts."""
        files = []

        # Prepare success rate data
        success_data = []
        for framework, summaries in aggregated.framework_summaries.items():
            total_files = sum(s.total_files for s in summaries)
            success_files = sum(s.successful_files for s in summaries)
            failed_files = sum(s.failed_files for s in summaries)

            success_data.append(
                {
                    "Framework": framework.value,
                    "Success Rate (%)": (success_files / total_files * 100) if total_files > 0 else 0,
                    "Total Files": total_files,
                    "Successful": success_files,
                    "Failed": failed_files,
                }
            )

        if not success_data:
            return files

        df = pd.DataFrame(success_data)

        # Success rate comparison
        fig = plt.figure(figsize=(10, 6))
        bars = plt.bar(df["Framework"], df["Success Rate (%)"])
        plt.title("Success Rate by Framework")
        plt.ylabel("Success Rate (%)")
        plt.xlabel("Framework")
        plt.xticks(rotation=45)
        plt.ylim(0, 100)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2.0, height + 1, f"{height:.1f}%", ha="center", va="bottom")

        plt.tight_layout()
        success_chart = self.output_dir / "success_rate_comparison.png"
        plt.savefig(success_chart, dpi=300, bbox_inches="tight")
        plt.close()
        files.append(success_chart)

        return files

    def _generate_resource_charts(self, aggregated: AggregatedResults) -> list[Path]:
        """Generate resource utilization charts."""
        files = []

        # Prepare resource data
        resource_data = []
        for framework, summaries in aggregated.framework_summaries.items():
            for summary in summaries:
                if summary.avg_peak_memory_mb is not None:
                    resource_data.append(
                        {
                            "Framework": framework.value,
                            "Category": summary.category.value,
                            "Peak Memory (MB)": summary.avg_peak_memory_mb,
                            "CPU Usage (%)": summary.avg_cpu_percent or 0,
                        }
                    )

        if not resource_data:
            return files

        df = pd.DataFrame(resource_data)

        # Memory usage chart
        fig = plt.figure(figsize=(12, 8))
        df_pivot = df.pivot(index="Framework", columns="Category", values="Peak Memory (MB)")
        ax = df_pivot.plot(kind="bar", ax=plt.gca())
        plt.title("Peak Memory Usage by Framework and Category")
        plt.ylabel("Memory (MB)")
        plt.xlabel("Framework")
        plt.xticks(rotation=45)
        plt.legend(title="Document Category")
        plt.tight_layout()

        memory_chart = self.output_dir / "memory_usage.png"
        plt.savefig(memory_chart, dpi=300, bbox_inches="tight")
        plt.close()
        files.append(memory_chart)

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
        category_data = []
        for category, summaries in aggregated.category_summaries.items():
            for summary in summaries:
                if summary.avg_extraction_time is not None:
                    category_data.append(
                        {
                            "Category": category.value,
                            "Framework": summary.framework.value,
                            "Avg Time (s)": summary.avg_extraction_time,
                            "Success Rate (%)": summary.success_rate * 100,
                            "Total Files": summary.total_files,
                        }
                    )

        if not category_data:
            return files

        df = pd.DataFrame(category_data)

        # Category difficulty analysis
        fig = plt.figure(figsize=(12, 8))
        category_avg = df.groupby("Category")["Avg Time (s)"].mean().sort_values(ascending=False)
        bars = plt.bar(category_avg.index, category_avg.values)
        plt.title("Average Processing Time by Document Category")
        plt.ylabel("Average Time (seconds)")
        plt.xlabel("Document Category")
        plt.xticks(rotation=45)

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2.0, height + 0.01, f"{height:.2f}s", ha="center", va="bottom")

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
        all_data = []
        for framework, summaries in aggregated.framework_summaries.items():
            for summary in summaries:
                all_data.append(
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
                )

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

    def generate_summary_metrics(self, aggregated_file: Path) -> dict[str, Any]:
        """Generate summary metrics for README."""
        with open(aggregated_file, "rb") as f:
            data = msgspec.json.decode(f.read())

        aggregated = AggregatedResults(**data) if isinstance(data, dict) else data

        # Calculate key metrics
        total_files = aggregated.total_files_processed
        total_time = aggregated.total_time_seconds
        frameworks_tested = len(aggregated.framework_summaries)
        categories_tested = len(aggregated.category_summaries)

        # Find best performing framework
        best_framework = None
        best_avg_time = float("inf")

        framework_stats = {}
        for framework, summaries in aggregated.framework_summaries.items():
            total_fw_files = sum(s.total_files for s in summaries)
            success_fw_files = sum(s.successful_files for s in summaries)
            success_rate = (success_fw_files / total_fw_files * 100) if total_fw_files > 0 else 0

            # Calculate average time across all categories
            times = [s.avg_extraction_time for s in summaries if s.avg_extraction_time is not None]
            avg_time = sum(times) / len(times) if times else float("inf")

            framework_stats[framework.value] = {
                "success_rate": success_rate,
                "avg_time": avg_time,
                "total_files": total_fw_files,
                "successful_files": success_fw_files,
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
