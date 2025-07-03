"""Enhanced HTML report generation for GitHub Pages deployment."""

from datetime import UTC, datetime
from pathlib import Path

from src.types import AggregatedResults


class EnhancedHTMLReporter:
    """Generate beautiful HTML reports for GitHub Pages."""

    def generate_html_report(self, results: AggregatedResults, output_path: Path) -> None:
        """Generate an enhanced HTML report with modern styling."""
        # Calculate summary metrics
        framework_metrics = self._calculate_framework_metrics(results)

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python Text Extraction Libraries Benchmarks 2025</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --primary: #3b82f6;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --dark: #1f2937;
            --light: #f3f4f6;
            --border: #e5e7eb;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #f9fafb;
            color: var(--dark);
            line-height: 1.6;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}

        header {{
            background: white;
            border-bottom: 1px solid var(--border);
            margin-bottom: 2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}

        .header-content {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }}

        h1 {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--dark);
            margin-bottom: 0.5rem;
        }}

        .subtitle {{
            color: #6b7280;
            font-size: 1rem;
        }}

        .github-link {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: var(--dark);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            text-decoration: none;
            font-weight: 500;
            transition: transform 0.2s;
        }}

        .github-link:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .metric-card {{
            background: white;
            border-radius: 0.5rem;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border: 1px solid var(--border);
        }}

        .metric-label {{
            font-size: 0.875rem;
            color: #6b7280;
            margin-bottom: 0.5rem;
        }}

        .metric-value {{
            font-size: 2rem;
            font-weight: 600;
            color: var(--primary);
        }}

        .metric-unit {{
            font-size: 1rem;
            color: #9ca3af;
            font-weight: 400;
        }}

        .section {{
            background: white;
            border-radius: 0.5rem;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border: 1px solid var(--border);
        }}

        h2 {{
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            color: var(--dark);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th {{
            background: var(--light);
            font-weight: 600;
            text-align: left;
            padding: 0.75rem 1rem;
            font-size: 0.875rem;
            color: var(--dark);
            border-bottom: 2px solid var(--border);
        }}

        td {{
            padding: 0.75rem 1rem;
            border-bottom: 1px solid var(--border);
        }}

        tr:hover {{
            background: #fafafa;
        }}

        .framework-badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 500;
        }}

        .badge-kreuzberg {{
            background: #e0e7ff;
            color: #4338ca;
        }}

        .badge-docling {{
            background: #dbeafe;
            color: #1e40af;
        }}

        .badge-markitdown {{
            background: #d1fae5;
            color: #047857;
        }}

        .badge-unstructured {{
            background: #fef3c7;
            color: #d97706;
        }}

        .success-rate {{
            font-weight: 600;
        }}

        .success {{ color: var(--success); }}
        .warning {{ color: var(--warning); }}
        .danger {{ color: var(--danger); }}

        .footer {{
            text-align: center;
            padding: 2rem;
            color: #6b7280;
            font-size: 0.875rem;
        }}

        .footer a {{
            color: var(--primary);
            text-decoration: none;
        }}

        .category-tabs {{
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
            border-bottom: 2px solid var(--border);
        }}

        .tab {{
            padding: 0.75rem 1.5rem;
            font-weight: 500;
            color: #6b7280;
            border-bottom: 2px solid transparent;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .tab.active {{
            color: var(--primary);
            border-bottom-color: var(--primary);
        }}

        .performance-bar {{
            background: var(--light);
            border-radius: 0.25rem;
            height: 8px;
            overflow: hidden;
            margin-top: 0.25rem;
        }}

        .performance-fill {{
            height: 100%;
            background: var(--success);
            transition: width 0.5s ease;
        }}

        .timestamp {{
            color: #9ca3af;
            font-size: 0.875rem;
            margin-top: 0.5rem;
        }}
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <div>
                <h1>Python Text Extraction Libraries Benchmarks 2025</h1>
                <p class="subtitle">Comprehensive performance comparison of popular text extraction frameworks</p>
                <p class="timestamp">Generated on {datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")}</p>
            </div>
            <a href="https://github.com/Goldziher/python-text-extraction-libs-benchmarks" class="github-link">
                <i class="fab fa-github"></i>
                View on GitHub
            </a>
        </div>
    </header>

    <div class="container">
        <!-- Summary Metrics -->
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Benchmarks</div>
                <div class="metric-value">{results.total_runs}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Files Processed</div>
                <div class="metric-value">{results.total_files_processed:,}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Runtime</div>
                <div class="metric-value">{results.total_time_seconds / 3600:.1f} <span class="metric-unit">hours</span></div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Frameworks Tested</div>
                <div class="metric-value">{len(results.framework_summaries)}</div>
            </div>
        </div>

        <!-- Framework Performance Summary -->
        <div class="section">
            <h2>📊 Framework Performance Overview</h2>
            <table>
                <thead>
                    <tr>
                        <th>Framework</th>
                        <th>Success Rate</th>
                        <th>Avg Time (s)</th>
                        <th>Memory (MB)</th>
                        <th>Throughput</th>
                    </tr>
                </thead>
                <tbody>
"""

        # Add framework rows
        for framework, metrics in framework_metrics.items():
            badge_class = f"badge-{framework.value.replace('_', '-')}"
            success_class = self._get_success_class(metrics["success_rate"])

            html_content += f"""
                    <tr>
                        <td><span class="framework-badge {badge_class}">{framework.value}</span></td>
                        <td class="success-rate {success_class}">{metrics["success_rate"]:.1f}%</td>
                        <td>{metrics["avg_time"]:.2f}</td>
                        <td>{metrics["avg_memory"]:.0f}</td>
                        <td>{metrics["throughput"]:.1f} files/s</td>
                    </tr>
"""

        html_content += """
                </tbody>
            </table>
        </div>

        <!-- Category Performance -->
        <div class="section">
            <h2>📁 Performance by Document Category</h2>
"""

        # Add category results
        from src.types import DocumentCategory

        for category in [DocumentCategory.TINY, DocumentCategory.SMALL, DocumentCategory.MEDIUM]:
            html_content += self._generate_category_section(results, category)

        html_content += """
        </div>

        <!-- Failure Analysis -->
"""

        if results.timeout_files or results.failure_patterns:
            html_content += self._generate_failure_section(results)

        html_content += """
    </div>

    <footer class="footer">
        <p>
            Generated by <a href="https://github.com/Goldziher/python-text-extraction-libs-benchmarks">Python Text Extraction Benchmarks</a>
            | View the <a href="benchmark_metrics.json">raw metrics</a>
            | <a href="https://github.com/Goldziher/python-text-extraction-libs-benchmarks/releases">Latest Release</a>
        </p>
    </footer>

    <script>
        // Simple tab functionality
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
            });
        });
    </script>
</body>
</html>
"""

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html_content)

    def _calculate_framework_metrics(self, results: AggregatedResults) -> dict:
        """Calculate aggregated metrics for each framework."""
        metrics = {}

        for framework, summaries in results.framework_summaries.items():
            if summaries:
                avg_success = sum(s.success_rate for s in summaries) / len(summaries)
                avg_times = [s.avg_extraction_time for s in summaries if s.avg_extraction_time]
                avg_time = sum(avg_times) / len(avg_times) if avg_times else 0
                avg_memories = [s.avg_peak_memory_mb for s in summaries if s.avg_peak_memory_mb]
                avg_memory = sum(avg_memories) / len(avg_memories) if avg_memories else 0
                avg_throughputs = [s.files_per_second for s in summaries if s.files_per_second]
                avg_throughput = sum(avg_throughputs) / len(avg_throughputs) if avg_throughputs else 0

                metrics[framework] = {
                    "success_rate": avg_success,
                    "avg_time": avg_time,
                    "avg_memory": avg_memory,
                    "throughput": avg_throughput,
                }

        return metrics

    def _get_success_class(self, rate: float) -> str:
        """Get CSS class based on success rate."""
        if rate >= 90:
            return "success"
        if rate >= 70:
            return "warning"
        return "danger"

    def _generate_category_section(self, results: AggregatedResults, category: object) -> str:
        """Generate HTML for a category section."""
        category_data = results.category_summaries.get(category, [])
        if not category_data:
            return ""

        html = f"""
            <h3 style="margin-top: 2rem; text-transform: capitalize;">{category.value} Documents</h3>
            <table>
                <thead>
                    <tr>
                        <th>Framework</th>
                        <th>Success Rate</th>
                        <th>Avg Time (s)</th>
                        <th>Total Files</th>
                    </tr>
                </thead>
                <tbody>
"""

        for summary in category_data:
            if summary.category == category:
                success_class = self._get_success_class(summary.success_rate)
                badge_class = f"badge-{summary.framework.value.replace('_', '-')}"

                html += f"""
                    <tr>
                        <td><span class="framework-badge {badge_class}">{summary.framework.value}</span></td>
                        <td class="success-rate {success_class}">{summary.success_rate:.1f}%</td>
                        <td>{summary.avg_extraction_time:.2f}</td>
                        <td>{summary.total_files}</td>
                    </tr>
"""

        html += """
                </tbody>
            </table>
"""
        return html

    def _generate_failure_section(self, results: AggregatedResults) -> str:
        """Generate failure analysis section."""
        html = """
        <div class="section">
            <h2>⚠️ Failure Analysis</h2>
"""

        if results.timeout_files:
            html += f"""
            <div class="metric-card" style="border-color: var(--warning);">
                <div class="metric-label">Timeout Files</div>
                <div class="metric-value" style="color: var(--warning);">{len(results.timeout_files)}</div>
                <p style="margin-top: 1rem; font-size: 0.875rem; color: #6b7280;">
                    Files that exceeded the 5-minute extraction timeout
                </p>
            </div>
"""

        if results.failure_patterns:
            html += """
            <h3 style="margin-top: 2rem;">Error Types</h3>
            <table>
                <thead>
                    <tr>
                        <th>Error Type</th>
                        <th>Count</th>
                    </tr>
                </thead>
                <tbody>
"""
            for error_type, count in sorted(results.failure_patterns.items(), key=lambda x: x[1], reverse=True):
                html += f"""
                    <tr>
                        <td><code>{error_type}</code></td>
                        <td>{count}</td>
                    </tr>
"""
            html += """
                </tbody>
            </table>
"""

        html += """
        </div>
"""
        return html
