"""Update README.md with latest benchmark results and visualizations."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def update_readme_with_results(
    readme_path: Path,
    summary_metrics: dict[str, Any],
    visualizations_dir: Path,  # noqa: ARG001
    run_id: str | None = None,
) -> None:
    """Update README.md with latest benchmark results."""
    # Read current README
    if readme_path.exists():
        with open(readme_path) as f:
            content = f.read()
    else:
        content = "# Python Text Extraction Libraries Benchmarks\n\n"

    # Generate timestamp
    timestamp = datetime.fromtimestamp(summary_metrics["timestamp"], tz=UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Create benchmark results section
    results_section = f"""
## 📊 Latest Benchmark Results

*Last updated: {timestamp}*
{f"*Run ID: {run_id}*" if run_id else ""}

### Summary

- **Total Files Processed:** {summary_metrics["total_files"]:,}
- **Total Processing Time:** {summary_metrics["total_time"]:.1f} seconds
- **Frameworks Tested:** {summary_metrics["frameworks_tested"]}
- **Document Categories:** {summary_metrics["categories_tested"]}
- **Best Performing Framework:** {summary_metrics["best_framework"] or "N/A"}

### Framework Performance

| Framework | Success Rate | Avg Time | Total Files | Status |
|-----------|--------------|----------|-------------|---------|
"""

    # Add framework stats
    for framework, stats in summary_metrics["framework_stats"].items():
        status = "🟢" if stats["success_rate"] > 90 else "🟡" if stats["success_rate"] > 70 else "🔴"
        results_section += f"| {framework} | {stats['success_rate']:.1f}% | {stats['avg_time']:.2f}s | {stats['total_files']} | {status} |\n"

    # Add visualizations section
    results_section += """
### Visualizations

📊 **[Interactive Dashboard](visualizations/interactive_dashboard.html)** - Comprehensive interactive analysis

#### Performance Charts
- ![Performance Comparison](visualizations/performance_comparison.png)
- ![Throughput Comparison](visualizations/throughput_comparison.png)

#### Analysis
- ![Success Rate Comparison](visualizations/success_rate_comparison.png)
- ![Performance Heatmap](visualizations/performance_heatmap.png)
- ![Memory Usage](visualizations/memory_usage.png)
- ![Category Analysis](visualizations/category_analysis.png)

### Download Reports

For detailed analysis, download the comprehensive reports:

- 📋 [Markdown Report](reports/benchmark_report.md)
- 📊 [JSON Metrics](reports/benchmark_metrics.json)
- 🌐 [HTML Report](reports/benchmark_report.html)

---
"""

    # Find existing results section and replace it
    start_marker = "## 📊 Latest Benchmark Results"
    end_marker = "---\n"

    start_idx = content.find(start_marker)
    if start_idx != -1:
        # Find the end of the results section
        temp_content = content[start_idx:]
        end_idx = temp_content.find(end_marker)
        if end_idx != -1:
            end_idx += len(end_marker)
            # Replace the existing section
            content = content[:start_idx] + results_section + content[start_idx + end_idx :]
        else:
            # No end marker found, replace everything after start marker
            content = content[:start_idx] + results_section
    else:
        # No existing results section, add after main heading
        lines = content.split("\n")
        insert_idx = 1  # After main heading
        for i, line in enumerate(lines):
            if line.startswith("#") and not line.startswith("##"):
                insert_idx = i + 1
                break

        lines.insert(insert_idx, results_section)
        content = "\n".join(lines)

    # Write updated README
    with open(readme_path, "w") as f:
        f.write(content)


def main() -> None:
    """Main function for CLI usage."""
    import click

    @click.command()
    @click.option(
        "--summary-file", type=click.Path(exists=True), required=True, help="Path to summary metrics JSON file"
    )
    @click.option("--readme-path", type=click.Path(), default="README.md", help="Path to README.md file")
    @click.option(
        "--visualizations-dir",
        type=click.Path(exists=True),
        default="visualizations",
        help="Path to visualizations directory",
    )
    @click.option("--run-id", help="GitHub Actions run ID")
    def update_readme(summary_file: str, readme_path: str, visualizations_dir: str, run_id: str | None) -> None:
        """Update README with benchmark results."""
        # Load summary metrics
        with open(summary_file) as f:
            summary_metrics = json.load(f)

        # Update README
        update_readme_with_results(Path(readme_path), summary_metrics, Path(visualizations_dir), run_id)

        print(f"✅ Updated {readme_path} with latest benchmark results")

    update_readme()


if __name__ == "__main__":
    main()
