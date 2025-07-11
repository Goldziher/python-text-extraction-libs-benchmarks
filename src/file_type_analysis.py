"""Per-file-type performance and quality analysis for text extraction benchmarks."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


class FileTypeAnalyzer:
    """Analyze benchmark results by file type for detailed insights."""

    def __init__(self, results_data: list[dict[str, Any]]) -> None:
        """Initialize with benchmark results data."""
        self.results = results_data
        self.file_type_stats = self._calculate_file_type_stats()

    def _calculate_file_type_stats(self) -> dict[str, dict[str, Any]]:
        """Calculate comprehensive statistics per file type and framework."""
        stats = defaultdict(
            lambda: defaultdict(
                lambda: {
                    "total_files": 0,
                    "successful_files": 0,
                    "failed_files": 0,
                    "timeout_files": 0,
                    "extraction_times": [],
                    "memory_usage": [],
                    "cpu_usage": [],
                    "character_counts": [],
                    "word_counts": [],
                    "file_sizes": [],
                }
            )
        )

        for result in self.results:
            file_type = result["file_type"]
            framework = result["framework"]

            stats[file_type][framework]["total_files"] += 1
            stats[file_type][framework]["file_sizes"].append(result["file_size"])

            if result["status"] == "success":
                stats[file_type][framework]["successful_files"] += 1
                stats[file_type][framework]["extraction_times"].append(result["extraction_time"])
                stats[file_type][framework]["memory_usage"].append(result["peak_memory_mb"])
                stats[file_type][framework]["cpu_usage"].append(result["avg_cpu_percent"])

                if result.get("character_count"):
                    stats[file_type][framework]["character_counts"].append(result["character_count"])
                if result.get("word_count"):
                    stats[file_type][framework]["word_counts"].append(result["word_count"])
            elif result["status"] == "failed":
                stats[file_type][framework]["failed_files"] += 1
            elif result["status"] == "timeout":
                stats[file_type][framework]["timeout_files"] += 1

        # Calculate aggregate metrics
        for file_type in stats:
            for framework in stats[file_type]:
                fw_stats = stats[file_type][framework]

                # Success rate
                fw_stats["success_rate"] = (
                    fw_stats["successful_files"] / fw_stats["total_files"] * 100 if fw_stats["total_files"] > 0 else 0
                )

                # Average metrics (only for successful extractions)
                fw_stats["avg_extraction_time"] = (
                    np.mean(fw_stats["extraction_times"]) if fw_stats["extraction_times"] else 0
                )
                fw_stats["avg_memory_mb"] = np.mean(fw_stats["memory_usage"]) if fw_stats["memory_usage"] else 0
                fw_stats["avg_cpu_percent"] = np.mean(fw_stats["cpu_usage"]) if fw_stats["cpu_usage"] else 0
                fw_stats["avg_file_size_mb"] = (
                    np.mean(fw_stats["file_sizes"]) / (1024 * 1024) if fw_stats["file_sizes"] else 0
                )

                # Throughput metrics
                fw_stats["files_per_second"] = (
                    1 / fw_stats["avg_extraction_time"] if fw_stats["avg_extraction_time"] > 0 else 0
                )
                fw_stats["mb_per_second"] = (
                    fw_stats["avg_file_size_mb"] / fw_stats["avg_extraction_time"]
                    if fw_stats["avg_extraction_time"] > 0
                    else 0
                )

                # Quality proxies
                fw_stats["avg_chars_per_file"] = (
                    np.mean(fw_stats["character_counts"]) if fw_stats["character_counts"] else 0
                )
                fw_stats["avg_words_per_file"] = np.mean(fw_stats["word_counts"]) if fw_stats["word_counts"] else 0

        return dict(stats)

    def generate_file_type_performance_report(self, output_dir: Path) -> None:
        """Generate comprehensive per-file-type performance report."""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create summary DataFrame
        summary_data = []
        for file_type, frameworks in self.file_type_stats.items():
            for framework, stats in frameworks.items():
                summary_data.append(
                    {
                        "file_type": file_type,
                        "framework": framework,
                        "total_files": stats["total_files"],
                        "success_rate": stats["success_rate"],
                        "avg_extraction_time": stats["avg_extraction_time"],
                        "avg_memory_mb": stats["avg_memory_mb"],
                        "files_per_second": stats["files_per_second"],
                        "avg_chars_per_file": stats["avg_chars_per_file"],
                        "avg_words_per_file": stats["avg_words_per_file"],
                    }
                )

        df = pd.DataFrame(summary_data)

        # Save CSV report
        df.to_csv(output_dir / "file_type_performance_summary.csv", index=False)

        # Generate visualizations
        self._create_success_rate_heatmap(df, output_dir)
        self._create_performance_by_file_type(df, output_dir)
        self._create_memory_usage_comparison(df, output_dir)
        self._create_throughput_analysis(df, output_dir)
        self._create_extraction_quality_analysis(df, output_dir)

        print(f"Generated file type analysis in {output_dir}")

    def _create_success_rate_heatmap(self, df: pd.DataFrame, output_dir: Path) -> None:
        """Create success rate heatmap by file type and framework."""
        pivot_data = df.pivot(index="file_type", columns="framework", values="success_rate")

        plt.figure(figsize=(14, 10))
        mask = pivot_data.isna()

        sns.heatmap(
            pivot_data,
            annot=True,
            fmt=".1f",
            cmap="RdYlGn",
            mask=mask,
            cbar_kws={"label": "Success Rate (%)"},
            linewidths=0.5,
        )

        plt.title("Success Rate by File Type and Framework", fontsize=16, fontweight="bold")
        plt.xlabel("Framework", fontsize=12)
        plt.ylabel("File Type", fontsize=12)
        plt.xticks(rotation=45, ha="right")
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.savefig(output_dir / "success_rate_by_file_type.png", dpi=300, bbox_inches="tight")
        plt.close()

    def _create_performance_by_file_type(self, df: pd.DataFrame, output_dir: Path) -> None:
        """Create performance comparison charts by file type."""
        file_types = df["file_type"].unique()
        n_types = len(file_types)

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle("Performance Metrics by File Type", fontsize=16, fontweight="bold")

        # Speed comparison
        ax1 = axes[0, 0]
        speed_data = df.pivot(index="file_type", columns="framework", values="files_per_second")
        speed_data.plot(kind="bar", ax=ax1, width=0.8)
        ax1.set_title("Processing Speed (Files/Second)")
        ax1.set_ylabel("Files per Second")
        ax1.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        ax1.tick_params(axis="x", rotation=45)

        # Memory usage
        ax2 = axes[0, 1]
        memory_data = df.pivot(index="file_type", columns="framework", values="avg_memory_mb")
        memory_data.plot(kind="bar", ax=ax2, width=0.8)
        ax2.set_title("Memory Usage (MB)")
        ax2.set_ylabel("Average Memory (MB)")
        ax2.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        ax2.tick_params(axis="x", rotation=45)

        # Success rate
        ax3 = axes[1, 0]
        success_data = df.pivot(index="file_type", columns="framework", values="success_rate")
        success_data.plot(kind="bar", ax=ax3, width=0.8)
        ax3.set_title("Success Rate (%)")
        ax3.set_ylabel("Success Rate (%)")
        ax3.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        ax3.tick_params(axis="x", rotation=45)

        # Extraction time
        ax4 = axes[1, 1]
        time_data = df.pivot(index="file_type", columns="framework", values="avg_extraction_time")
        time_data.plot(kind="bar", ax=ax4, width=0.8, logy=True)
        ax4.set_title("Average Extraction Time (seconds, log scale)")
        ax4.set_ylabel("Extraction Time (seconds)")
        ax4.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        ax4.tick_params(axis="x", rotation=45)

        plt.tight_layout()
        plt.savefig(output_dir / "performance_by_file_type.png", dpi=300, bbox_inches="tight")
        plt.close()

    def _create_memory_usage_comparison(self, df: pd.DataFrame, output_dir: Path) -> None:
        """Create detailed memory usage analysis by file type."""
        plt.figure(figsize=(14, 8))

        # Filter out frameworks with 0 memory usage (kreuzberg_async issue)
        df_filtered = df[df["avg_memory_mb"] > 0]

        sns.boxplot(data=df_filtered, x="file_type", y="avg_memory_mb", hue="framework")
        plt.title("Memory Usage Distribution by File Type", fontsize=16, fontweight="bold")
        plt.xlabel("File Type", fontsize=12)
        plt.ylabel("Average Memory Usage (MB)", fontsize=12)
        plt.xticks(rotation=45, ha="right")
        plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.tight_layout()
        plt.savefig(output_dir / "memory_usage_by_file_type.png", dpi=300, bbox_inches="tight")
        plt.close()

    def _create_throughput_analysis(self, df: pd.DataFrame, output_dir: Path) -> None:
        """Create throughput analysis showing framework efficiency per file type."""
        plt.figure(figsize=(14, 10))

        # Create scatter plot: x=avg_extraction_time, y=success_rate, size=total_files, color=framework
        frameworks = df["framework"].unique()
        colors = plt.cm.Set1(np.linspace(0, 1, len(frameworks)))

        for i, framework in enumerate(frameworks):
            fw_data = df[df["framework"] == framework]
            plt.scatter(
                fw_data["avg_extraction_time"],
                fw_data["success_rate"],
                s=fw_data["total_files"] * 10,  # Size based on number of files
                alpha=0.7,
                color=colors[i],
                label=framework,
            )

            # Add file type labels
            for _, row in fw_data.iterrows():
                plt.annotate(
                    row["file_type"],
                    (row["avg_extraction_time"], row["success_rate"]),
                    xytext=(5, 5),
                    textcoords="offset points",
                    fontsize=8,
                    alpha=0.8,
                )

        plt.xscale("log")
        plt.xlabel("Average Extraction Time (seconds, log scale)", fontsize=12)
        plt.ylabel("Success Rate (%)", fontsize=12)
        plt.title(
            "Framework Efficiency by File Type\n(Bubble size = number of files tested)", fontsize=14, fontweight="bold"
        )
        plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_dir / "throughput_efficiency_analysis.png", dpi=300, bbox_inches="tight")
        plt.close()

    def _create_extraction_quality_analysis(self, df: pd.DataFrame, output_dir: Path) -> None:
        """Create extraction quality analysis based on character/word counts."""
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))

        # Character count analysis
        ax1 = axes[0]
        df_chars = df[df["avg_chars_per_file"] > 0]  # Filter out zero values
        char_pivot = df_chars.pivot(index="file_type", columns="framework", values="avg_chars_per_file")
        char_pivot.plot(kind="bar", ax=ax1, width=0.8, logy=True)
        ax1.set_title("Average Characters Extracted per File Type", fontweight="bold")
        ax1.set_ylabel("Average Characters (log scale)")
        ax1.tick_params(axis="x", rotation=45)
        ax1.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

        # Word count analysis
        ax2 = axes[1]
        df_words = df[df["avg_words_per_file"] > 0]  # Filter out zero values
        word_pivot = df_words.pivot(index="file_type", columns="framework", values="avg_words_per_file")
        word_pivot.plot(kind="bar", ax=ax2, width=0.8, logy=True)
        ax2.set_title("Average Words Extracted per File Type", fontweight="bold")
        ax2.set_ylabel("Average Words (log scale)")
        ax2.tick_params(axis="x", rotation=45)
        ax2.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

        plt.suptitle("Content Extraction Quality by File Type", fontsize=16, fontweight="bold")
        plt.tight_layout()
        plt.savefig(output_dir / "extraction_quality_by_file_type.png", dpi=300, bbox_inches="tight")
        plt.close()

    def get_top_performing_frameworks(self, metric: str = "success_rate") -> dict[str, str]:
        """Get the top performing framework for each file type based on specified metric."""
        top_frameworks = {}

        for file_type, frameworks in self.file_type_stats.items():
            if not frameworks:
                continue

            best_framework = max(frameworks.items(), key=lambda x: x[1].get(metric, 0))

            top_frameworks[file_type] = {"framework": best_framework[0], "value": best_framework[1].get(metric, 0)}

        return top_frameworks

    def generate_insights_report(self, output_dir: Path) -> None:
        """Generate human-readable insights and recommendations."""
        insights = []

        # Top performers by metric
        insights.append("# File Type Performance Analysis - Key Insights\n")

        # Success rate leaders
        success_leaders = self.get_top_performing_frameworks("success_rate")
        insights.append("## 🏆 Success Rate Leaders by File Type\n")
        for file_type, data in success_leaders.items():
            insights.append(f"- **{file_type}**: {data['framework']} ({data['value']:.1f}%)")

        # Speed leaders
        speed_leaders = self.get_top_performing_frameworks("files_per_second")
        insights.append("\n## ⚡ Speed Leaders by File Type\n")
        for file_type, data in speed_leaders.items():
            insights.append(f"- **{file_type}**: {data['framework']} ({data['value']:.2f} files/sec)")

        # Memory efficiency leaders (lowest memory usage)
        memory_leaders = {}
        for file_type, frameworks in self.file_type_stats.items():
            if not frameworks:
                continue
            # Find framework with lowest memory usage (excluding 0 values)
            valid_frameworks = {k: v for k, v in frameworks.items() if v.get("avg_memory_mb", 0) > 0}
            if valid_frameworks:
                best_framework = min(valid_frameworks.items(), key=lambda x: x[1].get("avg_memory_mb", float("inf")))
                memory_leaders[file_type] = {
                    "framework": best_framework[0],
                    "value": best_framework[1].get("avg_memory_mb", 0),
                }

        insights.append("\n## 💾 Memory Efficiency Leaders by File Type\n")
        for file_type, data in memory_leaders.items():
            insights.append(f"- **{file_type}**: {data['framework']} ({data['value']:.1f} MB)")

        # Framework strengths and weaknesses
        insights.append("\n## 📊 Framework Specializations\n")

        framework_strengths = defaultdict(list)
        for file_type, data in success_leaders.items():
            framework_strengths[data["framework"]].append(file_type)

        for framework, file_types in framework_strengths.items():
            insights.append(f"- **{framework}**: Excels at {', '.join(file_types)}")

        # Save insights
        with open(output_dir / "performance_insights.md", "w") as f:
            f.write("\n".join(insights))


def main():
    """Main function to run file type analysis on existing benchmark data."""
    # Load data from existing results
    results_files = [
        "extractous-results/benchmark-extractous-tiny-16215030688/benchmark_results.json",
        "kreuzberg-results/benchmark-kreuzberg_sync-tiny-16215030688/benchmark_results.json",
        "kreuzberg-results/benchmark-kreuzberg_async-tiny-16215030688/benchmark_results.json",
        # Add more as needed
    ]

    all_results = []

    for file_path in results_files:
        path = Path(file_path)
        if path.exists():
            try:
                with open(path) as f:
                    data = json.load(f)
                    all_results.extend(data)
                    print(f"Loaded {len(data)} results from {file_path}")
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

    if not all_results:
        print("No results data found. Please ensure benchmark results exist.")
        return

    # Run analysis
    analyzer = FileTypeAnalyzer(all_results)
    output_dir = Path("file_type_analysis")

    analyzer.generate_file_type_performance_report(output_dir)
    analyzer.generate_insights_report(output_dir)

    print("\n✅ File type analysis complete!")
    print(f"📁 Results saved in: {output_dir}")
    print(f"📊 View charts: {output_dir}/*.png")
    print(f"📈 View insights: {output_dir}/performance_insights.md")


if __name__ == "__main__":
    main()
