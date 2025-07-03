"""Report generation for benchmark results."""

from __future__ import annotations

import json
from pathlib import Path

import msgspec

from src.types import AggregatedResults


class ReportGenerator:
    """Generate various report formats from aggregated results."""

    def load_results(self, results_dir: Path) -> AggregatedResults:
        """Load aggregated results from directory."""
        results_file = results_dir / "aggregated_results.json"
        if not results_file.exists():
            raise FileNotFoundError(f"Aggregated results not found: {results_file}")

        with open(results_file, "rb") as f:
            return msgspec.json.decode(f.read(), type=AggregatedResults)

    def generate_markdown_report(self, results: AggregatedResults, output_path: Path) -> None:
        """Generate a comprehensive markdown report."""
        lines = [
            "# Benchmark Report",
            "",
            f"**Total Runs:** {results.total_runs}",
            f"**Total Files Processed:** {results.total_files_processed}",
            f"**Total Time:** {results.total_time_seconds:.1f} seconds",
            "",
        ]

        # Framework Performance Summary
        lines.extend(
            [
                "## Framework Performance Summary",
                "",
                "| Framework | Avg Success Rate | Avg Time (s) | Avg Memory (MB) | Files/sec |",
                "|-----------|------------------|--------------|-----------------|-----------|",
            ]
        )

        for framework, summaries in results.framework_summaries.items():
            if summaries:
                avg_success = sum(s.success_rate for s in summaries) / len(summaries)
                avg_times = [s.avg_extraction_time for s in summaries if s.avg_extraction_time]
                avg_time = sum(avg_times) / len(avg_times) if avg_times else 0
                avg_memories = [s.avg_peak_memory_mb for s in summaries if s.avg_peak_memory_mb]
                avg_memory = sum(avg_memories) / len(avg_memories) if avg_memories else 0
                avg_throughputs = [s.files_per_second for s in summaries if s.files_per_second]
                avg_throughput = sum(avg_throughputs) / len(avg_throughputs) if avg_throughputs else 0

                lines.append(
                    f"| {framework.value} | {avg_success:.1%} | {avg_time:.2f} | {avg_memory:.1f} | {avg_throughput:.2f} |"
                )

        # Category Performance
        lines.extend(
            [
                "",
                "## Performance by Category",
                "",
            ]
        )

        for category, summaries in results.category_summaries.items():
            if summaries:
                lines.extend(
                    [
                        f"### {category.value.title()}",
                        "",
                        "| Framework | Success Rate | Avg Time (s) | Memory (MB) | Throughput |",
                        "|-----------|--------------|--------------|-------------|------------|",
                    ]
                )

                for summary in summaries:
                    success_rate = summary.success_rate
                    avg_time = summary.avg_extraction_time or 0
                    avg_memory = summary.avg_peak_memory_mb or 0
                    throughput = summary.files_per_second or 0

                    lines.append(
                        f"| {summary.framework.value} | {success_rate:.1%} | {avg_time:.2f} | {avg_memory:.1f} | {throughput:.2f} |"
                    )

                lines.append("")

        # Failure Analysis
        if results.failure_patterns:
            lines.extend(
                [
                    "## Failure Analysis",
                    "",
                    "| Error Type | Count |",
                    "|------------|-------|",
                ]
            )

            for error_type, count in sorted(results.failure_patterns.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"| {error_type} | {count} |")

            lines.append("")

        # Performance Trends
        if results.performance_over_iterations:
            lines.extend(
                [
                    "## Performance Trends Over Iterations",
                    "",
                ]
            )

            for framework, times in results.performance_over_iterations.items():
                if times:
                    lines.append(f"**{framework.value}:**")
                    for i, avg_time in enumerate(times, 1):
                        lines.append(f"- Iteration {i}: {avg_time:.2f}s")
                    lines.append("")

        # Platform Comparison
        if results.platform_results:
            lines.extend(
                [
                    "## Platform Comparison",
                    "",
                ]
            )

            for platform, platform_summaries in results.platform_results.items():
                lines.extend(
                    [
                        f"### {platform}",
                        "",
                        "| Framework | Success Rate | Avg Time (s) |",
                        "|-----------|--------------|--------------|",
                    ]
                )

                for framework, summary in platform_summaries.items():
                    success_rate = summary.success_rate
                    avg_time = summary.avg_extraction_time or 0
                    lines.append(f"| {framework.value} | {success_rate:.1%} | {avg_time:.2f} |")

                lines.append("")

        # Write report
        with open(output_path, "w") as f:
            f.write("\n".join(lines))

    def generate_json_metrics(self, results: AggregatedResults, output_path: Path) -> None:
        """Generate JSON metrics for GitHub Actions benchmark tracking."""
        metrics = []

        # Create metrics for each framework
        for framework, summaries in results.framework_summaries.items():
            if summaries:
                # Calculate overall metrics
                avg_success = sum(s.success_rate for s in summaries) / len(summaries)
                avg_times = [s.avg_extraction_time for s in summaries if s.avg_extraction_time]
                avg_time = sum(avg_times) / len(avg_times) if avg_times else 0
                avg_throughputs = [s.files_per_second for s in summaries if s.files_per_second]
                avg_throughput = sum(avg_throughputs) / len(avg_throughputs) if avg_throughputs else 0

                metrics.append(
                    {
                        "name": f"{framework.value} - Success Rate",
                        "unit": "percent",
                        "value": avg_success * 100,
                    }
                )

                metrics.append(
                    {
                        "name": f"{framework.value} - Avg Time",
                        "unit": "seconds",
                        "value": avg_time,
                    }
                )

                metrics.append(
                    {
                        "name": f"{framework.value} - Throughput",
                        "unit": "files/second",
                        "value": avg_throughput,
                    }
                )

        # Save metrics
        with open(output_path, "w") as f:
            json.dump(metrics, f, indent=2)

    def generate_html_report(self, results: AggregatedResults, output_path: Path) -> None:
        """Generate an HTML report with charts and tables."""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Benchmark Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1, h2, h3 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .metric {{ background-color: #e7f3ff; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .success {{ color: #28a745; }}
        .warning {{ color: #ffc107; }}
        .danger {{ color: #dc3545; }}
    </style>
</head>
<body>
    <h1>Benchmark Report</h1>

    <div class="metric">
        <strong>Total Runs:</strong> {results.total_runs}<br>
        <strong>Total Files Processed:</strong> {results.total_files_processed}<br>
        <strong>Total Time:</strong> {results.total_time_seconds:.1f} seconds
    </div>

    <h2>Framework Performance Summary</h2>
    <table>
        <tr>
            <th>Framework</th>
            <th>Avg Success Rate</th>
            <th>Avg Time (s)</th>
            <th>Avg Memory (MB)</th>
            <th>Files/sec</th>
        </tr>
"""

        for framework, summaries in results.framework_summaries.items():
            if summaries:
                avg_success = sum(s.success_rate for s in summaries) / len(summaries)
                avg_times = [s.avg_extraction_time for s in summaries if s.avg_extraction_time]
                avg_time = sum(avg_times) / len(avg_times) if avg_times else 0
                avg_memories = [s.avg_peak_memory_mb for s in summaries if s.avg_peak_memory_mb]
                avg_memory = sum(avg_memories) / len(avg_memories) if avg_memories else 0
                avg_throughputs = [s.files_per_second for s in summaries if s.files_per_second]
                avg_throughput = sum(avg_throughputs) / len(avg_throughputs) if avg_throughputs else 0

                success_class = "success" if avg_success > 0.9 else "warning" if avg_success > 0.7 else "danger"

                html_content += f"""
        <tr>
            <td>{framework.value}</td>
            <td class="{success_class}">{avg_success:.1%}</td>
            <td>{avg_time:.2f}</td>
            <td>{avg_memory:.1f}</td>
            <td>{avg_throughput:.2f}</td>
        </tr>"""

        html_content += """
    </table>

    <h2>Performance by Category</h2>
"""

        for category, summaries in results.category_summaries.items():
            if summaries:
                html_content += f"""
    <h3>{category.value.title()}</h3>
    <table>
        <tr>
            <th>Framework</th>
            <th>Success Rate</th>
            <th>Avg Time (s)</th>
            <th>Memory (MB)</th>
            <th>Throughput</th>
        </tr>
"""

                for summary in summaries:
                    success_rate = summary.success_rate
                    avg_time = summary.avg_extraction_time or 0
                    avg_memory = summary.avg_peak_memory_mb or 0
                    throughput = summary.files_per_second or 0

                    success_class = "success" if success_rate > 0.9 else "warning" if success_rate > 0.7 else "danger"

                    html_content += f"""
        <tr>
            <td>{summary.framework.value}</td>
            <td class="{success_class}">{success_rate:.1%}</td>
            <td>{avg_time:.2f}</td>
            <td>{avg_memory:.1f}</td>
            <td>{throughput:.2f}</td>
        </tr>"""

                html_content += """
    </table>
"""

        # Failure analysis
        if results.failure_patterns:
            html_content += """
    <h2>Failure Analysis</h2>
    <table>
        <tr>
            <th>Error Type</th>
            <th>Count</th>
        </tr>
"""

            for error_type, count in sorted(results.failure_patterns.items(), key=lambda x: x[1], reverse=True):
                html_content += f"""
        <tr>
            <td>{error_type}</td>
            <td>{count}</td>
        </tr>"""

            html_content += """
    </table>
"""

        html_content += """
</body>
</html>
"""

        with open(output_path, "w") as f:
            f.write(html_content)
