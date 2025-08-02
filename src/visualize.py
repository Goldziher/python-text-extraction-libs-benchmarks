"""Visualization module for benchmark results."""
# ruff: noqa: PERF401, PLR0915

from __future__ import annotations

from pathlib import Path

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
    "kreuzberg_tesseract": "#4A7C7E",  # Teal
    "kreuzberg_easyocr": "#8B5A3C",  # Brown
    "kreuzberg_easyocr_sync": "#8B5A3C",  # Brown (same as async variant)
    "kreuzberg_paddleocr": "#6A5ACD",  # Slate Blue
    "kreuzberg_paddleocr_sync": "#6A5ACD",  # Slate Blue (same as async variant)
    "docling": "#F18F01",  # Orange
    "markitdown": "#C73E1D",  # Red
    "unstructured": "#5B9A8B",  # Green
    "extractous": "#FF6B35",  # Orange-red (Rust color theme)
}


class BenchmarkVisualizer:
    """Generate comprehensive visualizations from benchmark results."""

    def __init__(self, output_dir: Path = Path("results/charts")) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set style for matplotlib/seaborn with larger default sizes
        plt.style.use("default")
        plt.rcParams.update(
            {
                "figure.dpi": 150,
                "savefig.dpi": 150,
                "font.size": 12,
                "axes.titlesize": 16,
                "axes.labelsize": 14,
                "xtick.labelsize": 12,
                "ytick.labelsize": 12,
                "legend.fontsize": 12,
            }
        )

        # Set consistent color palette for frameworks
        framework_colors = list(FRAMEWORK_COLORS.values())
        sns.set_palette(framework_colors)

    def generate_all_visualizations(self, aggregated_file: Path) -> list[Path]:
        """Generate all visualizations from aggregated results."""
        # Load data
        with open(aggregated_file, "rb") as f:
            aggregated = msgspec.json.decode(f.read(), type=AggregatedResults)

        output_files = []

        # Generate individual visualizations
        output_files.extend(self._create_performance_comparison(aggregated))
        output_files.extend(self._create_memory_usage_charts(aggregated))
        output_files.extend(self._create_success_rate_chart(aggregated))
        output_files.extend(self._create_throughput_charts(aggregated))
        output_files.extend(self._create_per_file_breakdown(aggregated))
        output_files.extend(self._create_category_analysis(aggregated))
        output_files.append(self._create_interactive_dashboard(aggregated))

        return output_files

    def _create_performance_comparison(self, aggregated: AggregatedResults) -> list[Path]:
        """Create performance comparison charts."""
        output_files = []

        # Extract data for visualization - flatten framework summaries
        all_summaries = []
        for fw_summaries in aggregated.framework_summaries.values():
            all_summaries.extend(fw_summaries)

        perf_data = []
        for summary in all_summaries:
            if summary.total_files > 0:
                perf_data.append(
                    {
                        "Framework": str(summary.framework.value)
                        if hasattr(summary.framework, "value")
                        else str(summary.framework),
                        "Category": str(summary.category.value)
                        if hasattr(summary.category, "value")
                        else str(summary.category),
                        "Avg Time (s)": summary.avg_extraction_time,
                        "Median Time (s)": summary.median_extraction_time,
                        "Files per Second": summary.files_per_second,
                        "Success Rate (%)": (summary.success_rate * 100) if summary.success_rate is not None else 0,
                    }
                )

        if not perf_data:
            return output_files

        df = pd.DataFrame(perf_data)

        # 1. Large performance comparison by category
        fig = plt.figure(figsize=(20, 12))
        df_pivot = df.pivot(index="Framework", columns="Category", values="Avg Time (s)")

        ax = df_pivot.plot(kind="bar", width=0.8, figsize=(20, 12))
        plt.title("Average Extraction Time by Framework and Category", fontsize=20, fontweight="bold", pad=20)
        plt.xlabel("Framework", fontsize=16)
        plt.ylabel("Average Time (seconds)", fontsize=16)
        plt.yscale("log")
        plt.grid(True, alpha=0.3, axis="y")
        plt.legend(title="Category", bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=14)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        output_path = self.output_dir / "performance_comparison_large.png"
        plt.savefig(output_path, bbox_inches="tight", dpi=150)
        plt.close()
        output_files.append(output_path)

        # 2. Performance by size category (focused view)
        size_categories = ["tiny", "small", "medium", "large", "huge"]
        df_sizes = df[df["Category"].isin(size_categories)]

        if not df_sizes.empty:
            fig, axes = plt.subplots(2, 3, figsize=(24, 16))
            axes = axes.flatten()

            for idx, category in enumerate(size_categories):
                ax = axes[idx]
                cat_data = df_sizes[df_sizes["Category"] == category].sort_values("Avg Time (s)")

                if not cat_data.empty:
                    bars = ax.bar(
                        cat_data["Framework"],
                        cat_data["Avg Time (s)"],
                        color=[FRAMEWORK_COLORS.get(fw, "#999999") for fw in cat_data["Framework"]],
                    )
                    ax.set_title(f"{category.title()} Files", fontsize=16, fontweight="bold")
                    ax.set_ylabel("Average Time (s)", fontsize=14)
                    ax.set_yscale("log")
                    ax.grid(True, alpha=0.3, axis="y")
                    ax.tick_params(axis="x", rotation=45)

                    # Add value labels on bars
                    for bar, val in zip(bars, cat_data["Avg Time (s)"], strict=False):
                        ax.text(
                            bar.get_x() + bar.get_width() / 2,
                            bar.get_height(),
                            f"{val:.3f}s",
                            ha="center",
                            va="bottom",
                            fontsize=10,
                        )

            # Hide the 6th subplot
            axes[5].axis("off")

            plt.suptitle("Performance Comparison by File Size Category", fontsize=20, fontweight="bold")
            plt.tight_layout()

            output_path = self.output_dir / "performance_by_size_category.png"
            plt.savefig(output_path, bbox_inches="tight", dpi=150)
            plt.close()
            output_files.append(output_path)

        return output_files

    def _create_memory_usage_charts(self, aggregated: AggregatedResults) -> list[Path]:
        """Create memory usage visualizations."""
        output_files = []

        # Extract memory data
        memory_data = []
        # Flatten framework summaries
        all_summaries = []
        for fw_summaries in aggregated.framework_summaries.values():
            all_summaries.extend(fw_summaries)

        for summary in all_summaries:
            if summary.avg_peak_memory_mb and summary.avg_peak_memory_mb > 0:
                memory_data.append(
                    {
                        "Framework": str(summary.framework.value)
                        if hasattr(summary.framework, "value")
                        else str(summary.framework),
                        "Category": str(summary.category.value)
                        if hasattr(summary.category, "value")
                        else str(summary.category),
                        "Avg Memory (MB)": summary.avg_peak_memory_mb,
                        "CPU Usage (%)": summary.avg_cpu_percent,
                    }
                )

        if not memory_data:
            return output_files

        df = pd.DataFrame(memory_data)

        # Create large dual-axis chart
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 16))

        # Memory usage heatmap
        df_pivot = df.pivot(index="Framework", columns="Category", values="Avg Memory (MB)")
        sns.heatmap(df_pivot, annot=True, fmt=".0f", cmap="YlOrRd", ax=ax1, cbar_kws={"label": "Memory Usage (MB)"})
        ax1.set_title("Average Peak Memory Usage by Framework and Category", fontsize=18, fontweight="bold", pad=15)
        ax1.set_xlabel("")

        # CPU usage heatmap
        df_pivot_cpu = df.pivot(index="Framework", columns="Category", values="CPU Usage (%)")
        sns.heatmap(df_pivot_cpu, annot=True, fmt=".1f", cmap="Blues", ax=ax2, cbar_kws={"label": "CPU Usage (%)"})
        ax2.set_title("Average CPU Usage by Framework and Category", fontsize=18, fontweight="bold", pad=15)

        plt.tight_layout()
        output_path = self.output_dir / "resource_usage_heatmaps.png"
        plt.savefig(output_path, bbox_inches="tight", dpi=150)
        plt.close()
        output_files.append(output_path)

        return output_files

    def _create_success_rate_chart(self, aggregated: AggregatedResults) -> list[Path]:
        """Create success rate visualization."""
        output_files = []

        # Calculate overall success rates
        framework_stats = {}
        # Flatten framework summaries
        all_summaries = []
        for fw_summaries in aggregated.framework_summaries.values():
            all_summaries.extend(fw_summaries)

        for summary in all_summaries:
            framework_key = summary.framework.value if hasattr(summary.framework, "value") else str(summary.framework)
            if framework_key not in framework_stats:
                framework_stats[framework_key] = {
                    "total": 0,
                    "successful": 0,
                    "failed": 0,
                    "timeout": 0,
                }

            stats = framework_stats[framework_key]
            stats["total"] += summary.total_files
            stats["successful"] += summary.successful_files
            stats["failed"] += summary.failed_files
            stats["timeout"] += summary.timeout_files

        # Create detailed success chart
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

        # Overall success rates
        frameworks = list(framework_stats.keys())
        success_rates = [
            (stats["successful"] / stats["total"] * 100) if stats["total"] > 0 else 0
            for stats in framework_stats.values()
        ]

        bars = ax1.bar(frameworks, success_rates, color=[FRAMEWORK_COLORS.get(fw, "#999999") for fw in frameworks])
        ax1.set_title("Overall Success Rate by Framework", fontsize=18, fontweight="bold")
        ax1.set_ylabel("Success Rate (%)", fontsize=14)
        ax1.set_ylim(0, 105)
        ax1.grid(True, alpha=0.3, axis="y")

        # Add value labels
        for bar, rate in zip(bars, success_rates, strict=False):
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1,
                f"{rate:.1f}%",
                ha="center",
                va="bottom",
                fontsize=12,
            )

        ax1.tick_params(axis="x", rotation=45)

        # Failure breakdown
        failure_data = []
        for fw, stats in framework_stats.items():
            if stats["failed"] > 0 or stats["timeout"] > 0:
                failure_data.append(
                    {
                        "Framework": fw,
                        "Failed": stats["failed"],
                        "Timeout": stats["timeout"],
                    }
                )

        if failure_data:
            df_failures = pd.DataFrame(failure_data)
            df_failures.set_index("Framework")[["Failed", "Timeout"]].plot(
                kind="bar", stacked=True, ax=ax2, color=["#ef4444", "#f59e0b"]
            )
            ax2.set_title("Failure Breakdown by Type", fontsize=18, fontweight="bold")
            ax2.set_ylabel("Number of Files", fontsize=14)
            ax2.tick_params(axis="x", rotation=45)
            ax2.legend(title="Failure Type")
        else:
            ax2.text(
                0.5,
                0.5,
                "No failures detected!",
                transform=ax2.transAxes,
                ha="center",
                va="center",
                fontsize=20,
                fontweight="bold",
                color="green",
            )
            ax2.set_xticks([])
            ax2.set_yticks([])

        plt.tight_layout()
        output_path = self.output_dir / "success_and_failure_analysis.png"
        plt.savefig(output_path, bbox_inches="tight", dpi=150)
        plt.close()
        output_files.append(output_path)

        return output_files

    def _create_throughput_charts(self, aggregated: AggregatedResults) -> list[Path]:
        """Create throughput visualizations."""
        output_files = []

        throughput_data = []
        # Flatten framework summaries
        all_summaries = []
        for fw_summaries in aggregated.framework_summaries.values():
            all_summaries.extend(fw_summaries)

        for summary in all_summaries:
            if summary.mb_per_second and summary.mb_per_second > 0:
                throughput_data.append(
                    {
                        "Framework": str(summary.framework.value)
                        if hasattr(summary.framework, "value")
                        else str(summary.framework),
                        "Category": str(summary.category.value)
                        if hasattr(summary.category, "value")
                        else str(summary.category),
                        "Files/Second": summary.files_per_second,
                        "MB/Second": summary.mb_per_second,
                    }
                )

        if not throughput_data:
            return output_files

        df = pd.DataFrame(throughput_data)

        # Create comprehensive throughput visualization
        fig = plt.figure(figsize=(22, 14))

        # Create subplot layout
        gs = fig.add_gridspec(2, 2, height_ratios=[1, 1], width_ratios=[3, 2])
        ax1 = fig.add_subplot(gs[0, :])
        ax2 = fig.add_subplot(gs[1, 0])
        ax3 = fig.add_subplot(gs[1, 1])

        # Main throughput comparison
        df_pivot = df.pivot(index="Framework", columns="Category", values="MB/Second")
        df_pivot.plot(kind="bar", ax=ax1, width=0.8)
        ax1.set_title("Data Throughput by Framework and Category", fontsize=18, fontweight="bold")
        ax1.set_ylabel("Throughput (MB/s)", fontsize=14)
        ax1.set_yscale("log")
        ax1.grid(True, alpha=0.3, axis="y")
        ax1.legend(title="Category", bbox_to_anchor=(1.05, 1), loc="upper left")
        ax1.tick_params(axis="x", rotation=45)

        # Files per second for size categories
        size_cats = ["tiny", "small", "medium", "large", "huge"]
        df_sizes = df[df["Category"].isin(size_cats)]
        if not df_sizes.empty:
            df_pivot_files = df_sizes.pivot(index="Framework", columns="Category", values="Files/Second")
            df_pivot_files.plot(kind="bar", ax=ax2, width=0.8)
            ax2.set_title("Files Processed per Second (Size Categories)", fontsize=16, fontweight="bold")
            ax2.set_ylabel("Files/Second", fontsize=14)
            ax2.set_yscale("log")
            ax2.grid(True, alpha=0.3, axis="y")
            ax2.tick_params(axis="x", rotation=45)
            ax2.legend(title="Category")

        # Average throughput summary
        avg_throughput = df.groupby("Framework")["MB/Second"].mean().sort_values(ascending=False)
        bars = ax3.barh(
            avg_throughput.index,
            avg_throughput.values,
            color=[FRAMEWORK_COLORS.get(fw, "#999999") for fw in avg_throughput.index],
        )
        ax3.set_title("Average Throughput Across All Categories", fontsize=16, fontweight="bold")
        ax3.set_xlabel("Average MB/Second", fontsize=14)
        ax3.grid(True, alpha=0.3, axis="x")

        # Add value labels
        for bar, val in zip(bars, avg_throughput.values, strict=False):
            ax3.text(
                bar.get_width() + val * 0.01,
                bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}",
                ha="left",
                va="center",
                fontsize=11,
            )

        plt.tight_layout()
        output_path = self.output_dir / "throughput_analysis_comprehensive.png"
        plt.savefig(output_path, bbox_inches="tight", dpi=150)
        plt.close()
        output_files.append(output_path)

        return output_files

    def _create_per_file_breakdown(self, aggregated: AggregatedResults) -> list[Path]:
        """Create per-file performance breakdown charts."""
        # Skip - individual results not available in aggregated data
        # This would require access to the detailed benchmark results
        return []

    def _create_category_analysis(self, aggregated: AggregatedResults) -> list[Path]:  # noqa: C901, PLR0912
        """Create comprehensive category analysis."""
        output_files = []

        # Aggregate data by category
        category_data = {}
        # Flatten framework summaries
        all_summaries = []
        for fw_summaries in aggregated.framework_summaries.values():
            all_summaries.extend(fw_summaries)

        for summary in all_summaries:
            cat = summary.category
            if cat not in category_data:
                category_data[cat] = {
                    "frameworks": [],
                    "avg_times": [],
                    "success_rates": [],
                    "throughputs": [],
                }

            category_data[cat]["frameworks"].append(
                summary.framework.value if hasattr(summary.framework, "value") else str(summary.framework)
            )
            category_data[cat]["avg_times"].append(summary.avg_extraction_time)
            category_data[cat]["success_rates"].append(summary.success_rate)
            category_data[cat]["throughputs"].append(summary.mb_per_second or 0)

        # Create comprehensive category comparison
        fig = plt.figure(figsize=(24, 20))
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.2)

        # 1. Average time by category
        ax1 = fig.add_subplot(gs[0, :])
        categories = list(category_data.keys())
        avg_times_per_cat = []
        for d in category_data.values():
            valid_times = [t for t in d["avg_times"] if t is not None]
            if valid_times:
                avg_times_per_cat.append(sum(valid_times) / len(valid_times))
            else:
                avg_times_per_cat.append(0)

        bars = ax1.bar(categories, avg_times_per_cat, color="skyblue", edgecolor="navy")
        ax1.set_title("Average Extraction Time by Category (All Frameworks)", fontsize=18, fontweight="bold")
        ax1.set_ylabel("Average Time (seconds)", fontsize=14)
        ax1.set_yscale("log")
        ax1.grid(True, alpha=0.3, axis="y")
        ax1.tick_params(axis="x", rotation=45)

        # Add value labels
        for bar, val in zip(bars, avg_times_per_cat, strict=False):
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{val:.3f}s",
                ha="center",
                va="bottom",
                fontsize=10,
            )

        # 2. Success rate distribution
        ax2 = fig.add_subplot(gs[1, 0])
        success_data = []
        for cat, data in category_data.items():
            for rate in data["success_rates"]:
                if rate is not None:
                    success_data.append({"Category": cat, "Success Rate": rate * 100})

        df_success = pd.DataFrame(success_data)
        df_success.boxplot(column="Success Rate", by="Category", ax=ax2)
        ax2.set_title("Success Rate Distribution by Category", fontsize=16, fontweight="bold")
        ax2.set_ylabel("Success Rate (%)", fontsize=14)
        ax2.set_xlabel("")
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

        # 3. Throughput distribution
        ax3 = fig.add_subplot(gs[1, 1])
        throughput_data = []
        for cat, data in category_data.items():
            for tp in data["throughputs"]:
                if tp > 0:
                    throughput_data.append({"Category": cat, "Throughput": tp})

        if throughput_data:
            df_throughput = pd.DataFrame(throughput_data)
            df_throughput.boxplot(column="Throughput", by="Category", ax=ax3)
            ax3.set_title("Throughput Distribution by Category", fontsize=16, fontweight="bold")
            ax3.set_ylabel("Throughput (MB/s)", fontsize=14)
            ax3.set_yscale("log")
            ax3.set_xlabel("")
            plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)

        # 4. Framework performance heatmap by category
        ax4 = fig.add_subplot(gs[2, :])

        # Create performance matrix
        frameworks = sorted({fw for data in category_data.values() for fw in data["frameworks"]})
        categories = sorted(category_data.keys())

        perf_matrix = []
        for fw in frameworks:
            row = []
            for cat in categories:
                if fw in category_data[cat]["frameworks"]:
                    idx = category_data[cat]["frameworks"].index(fw)
                    time = category_data[cat]["avg_times"][idx]
                    row.append(time)
                else:
                    row.append(None)
            perf_matrix.append(row)

        # Convert to numpy array and create heatmap
        import numpy as np

        perf_array = np.array([[x if x is not None else np.nan for x in row] for row in perf_matrix])

        sns.heatmap(
            perf_array,
            xticklabels=categories,
            yticklabels=frameworks,
            annot=True,
            fmt=".3f",
            cmap="YlOrRd",
            cbar_kws={"label": "Average Time (seconds)"},
            ax=ax4,
        )
        ax4.set_title("Framework Performance Heatmap by Category", fontsize=16, fontweight="bold")

        plt.suptitle("Comprehensive Category Analysis", fontsize=22, fontweight="bold")
        plt.tight_layout()

        output_path = self.output_dir / "category_analysis_comprehensive.png"
        plt.savefig(output_path, bbox_inches="tight", dpi=150)
        plt.close()
        output_files.append(output_path)

        return output_files

    def _create_interactive_dashboard(self, aggregated: AggregatedResults) -> Path:
        """Create an interactive Plotly dashboard."""
        # Create subplots
        fig = make_subplots(
            rows=3,
            cols=2,
            subplot_titles=(
                "Average Extraction Time by Framework",
                "Memory Usage Distribution",
                "Success Rate Comparison",
                "Throughput Analysis",
                "Category Performance Heatmap",
                "File Size vs. Extraction Time",
            ),
            specs=[
                [{"type": "bar"}, {"type": "box"}],
                [{"type": "bar"}, {"type": "scatter"}],
                [{"type": "heatmap"}, {"type": "scatter"}],
            ],
            vertical_spacing=0.12,
            horizontal_spacing=0.1,
        )

        # Prepare data
        perf_data = []
        # Flatten framework summaries
        all_summaries = []
        for fw_summaries in aggregated.framework_summaries.values():
            all_summaries.extend(fw_summaries)

        for summary in all_summaries:
            perf_data.append(
                {
                    "framework": str(summary.framework.value)
                    if hasattr(summary.framework, "value")
                    else str(summary.framework),
                    "category": str(summary.category.value)
                    if hasattr(summary.category, "value")
                    else str(summary.category),
                    "avg_time": summary.avg_extraction_time,
                    "memory": summary.avg_peak_memory_mb or 0,
                    "success_rate": (summary.success_rate * 100) if summary.success_rate is not None else 0,
                    "throughput": summary.mb_per_second or 0,
                }
            )

        df = pd.DataFrame(perf_data)

        # 1. Average extraction time
        for fw in df["framework"].unique():
            fw_data = df[df["framework"] == fw]
            fig.add_trace(
                go.Bar(
                    name=fw,
                    x=fw_data["category"],
                    y=fw_data["avg_time"],
                    marker_color=FRAMEWORK_COLORS.get(fw, "#999999"),
                ),
                row=1,
                col=1,
            )

        # 2. Memory usage distribution
        for fw in df["framework"].unique():
            fw_data = df[df["framework"] == fw]
            if fw_data["memory"].sum() > 0:
                fig.add_trace(
                    go.Box(name=fw, y=fw_data["memory"], marker_color=FRAMEWORK_COLORS.get(fw, "#999999")), row=1, col=2
                )

        # 3. Success rate comparison
        fw_success = df.groupby("framework")["success_rate"].mean()
        fig.add_trace(
            go.Bar(
                x=fw_success.index,
                y=fw_success.values,
                marker_color=[FRAMEWORK_COLORS.get(fw, "#999999") for fw in fw_success.index],
                showlegend=False,
            ),
            row=2,
            col=1,
        )

        # 4. Throughput scatter
        fig.add_trace(
            go.Scatter(
                x=df["avg_time"],
                y=df["throughput"],
                mode="markers",
                marker={
                    "size": 10,
                    "color": [FRAMEWORK_COLORS.get(fw, "#999999") for fw in df["framework"]],
                    "line": {"width": 1, "color": "white"},
                },
                text=df["framework"] + " - " + df["category"],
                showlegend=False,
            ),
            row=2,
            col=2,
        )

        # 5. Performance heatmap
        pivot_table = df.pivot_table(values="avg_time", index="framework", columns="category")
        fig.add_trace(
            go.Heatmap(
                z=pivot_table.values, x=pivot_table.columns, y=pivot_table.index, colorscale="YlOrRd", showscale=True
            ),
            row=3,
            col=1,
        )

        # 6. File size vs extraction time (skip - requires detailed results)
        # This would require access to individual benchmark results

        # Update layout
        fig.update_layout(
            height=1800,
            showlegend=True,
            title={"text": "Python Text Extraction Benchmarks - Interactive Dashboard", "font": {"size": 24}},
        )

        # Update axes
        fig.update_xaxes(title_text="Category", row=1, col=1)
        fig.update_yaxes(title_text="Time (s)", type="log", row=1, col=1)

        fig.update_yaxes(title_text="Memory (MB)", row=1, col=2)

        fig.update_xaxes(title_text="Framework", row=2, col=1)
        fig.update_yaxes(title_text="Success Rate (%)", row=2, col=1)

        fig.update_xaxes(title_text="Avg Time (s)", type="log", row=2, col=2)
        fig.update_yaxes(title_text="Throughput (MB/s)", type="log", row=2, col=2)

        fig.update_xaxes(title_text="File Size (MB)", type="log", row=3, col=2)
        fig.update_yaxes(title_text="Extraction Time (s)", type="log", row=3, col=2)

        # Save interactive HTML
        output_path = self.output_dir / "interactive_dashboard.html"
        fig.write_html(str(output_path), include_plotlyjs="cdn")

        return output_path

    def generate_summary_metrics(self, aggregated_file: Path) -> dict:
        """Generate summary metrics from aggregated results."""
        with open(aggregated_file, "rb") as f:
            aggregated = msgspec.json.decode(f.read(), type=AggregatedResults)

        # Flatten all summaries
        all_summaries = []
        for fw_summaries in aggregated.framework_summaries.values():
            all_summaries.extend(fw_summaries)

        # Calculate overall metrics
        metrics = {
            "total_runs": aggregated.total_runs,
            "total_files_processed": aggregated.total_files_processed,
            "total_time_seconds": aggregated.total_time_seconds,
            "frameworks_tested": len(aggregated.framework_summaries),
            "framework_performance": {},
            "category_performance": {},
        }

        # Framework performance
        for framework, summaries in aggregated.framework_summaries.items():
            total_files = sum(s.total_files for s in summaries)
            successful_files = sum(s.successful_files for s in summaries)
            avg_speed = (
                sum((s.files_per_second or 0) * s.total_files for s in summaries) / total_files
                if total_files > 0
                else 0
            )
            avg_memory = (
                sum((s.avg_peak_memory_mb or 0) * s.total_files for s in summaries) / total_files
                if total_files > 0
                else 0
            )

            metrics["framework_performance"][framework] = {
                "total_files": total_files,
                "successful_files": successful_files,
                "success_rate": successful_files / total_files if total_files > 0 else 0,
                "avg_files_per_second": avg_speed,
                "avg_memory_mb": avg_memory,
            }

        # Category performance
        for category, summaries in aggregated.category_summaries.items():
            total_files = sum(s.total_files for s in summaries)
            successful_files = sum(s.successful_files for s in summaries)

            metrics["category_performance"][category] = {
                "total_files": total_files,
                "successful_files": successful_files,
                "success_rate": successful_files / total_files if total_files > 0 else 0,
            }

        return metrics
