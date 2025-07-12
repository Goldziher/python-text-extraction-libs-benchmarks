"""HTML report generation with comprehensive layout and per-file breakdowns."""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import msgspec

from src.types import AggregatedResults


class HTMLReportGenerator:
    """Generate comprehensive HTML reports."""

    def __init__(self, charts_dir: Path = Path("results/charts")) -> None:
        self.charts_dir = charts_dir

    def generate_report(self, aggregated_file: Path, output_path: Path) -> None:
        """Generate HTML report."""
        # Load data
        with open(aggregated_file, "rb") as f:
            aggregated = msgspec.json.decode(f.read(), type=AggregatedResults)

        # Generate HTML content
        html_content = self._generate_html(aggregated)

        # Write to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

    def _generate_html(self, aggregated: AggregatedResults) -> str:
        """Generate the complete HTML report."""
        # Calculate summary metrics
        total_files = sum(s.total_files for s in aggregated.summaries)
        total_successful = sum(s.successful_files for s in aggregated.summaries)
        overall_success_rate = (total_successful / total_files * 100) if total_files > 0 else 0

        # Get framework performance summary
        framework_summary = self._get_framework_summary(aggregated)

        # Get per-file breakdowns
        file_breakdowns = self._get_file_breakdowns(aggregated)

        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python Text Extraction Libraries Benchmarks 2025 - Enhanced Report</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --primary: #3b82f6;
            --primary-dark: #2563eb;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --dark: #1f2937;
            --gray-100: #f3f4f6;
            --gray-200: #e5e7eb;
            --gray-300: #d1d5db;
            --gray-600: #4b5563;
            --gray-700: #374151;
            --shadow: 0 1px 3px rgba(0,0,0,0.1);
            --shadow-lg: 0 10px 25px rgba(0,0,0,0.1);
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

        /* Header Styles */
        header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white;
            padding: 3rem 0;
            box-shadow: var(--shadow-lg);
        }}

        .header-content {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 2rem;
        }}

        h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
        }}

        .subtitle {{
            font-size: 1.25rem;
            opacity: 0.9;
            margin-bottom: 2rem;
        }}

        .header-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }}

        .stat-card {{
            background: rgba(255, 255, 255, 0.1);
            padding: 1.5rem;
            border-radius: 0.75rem;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        .stat-value {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }}

        .stat-label {{
            font-size: 0.875rem;
            opacity: 0.8;
        }}

        /* Navigation */
        nav {{
            background: white;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: var(--shadow);
        }}

        .nav-content {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 2rem;
            display: flex;
            gap: 2rem;
            overflow-x: auto;
        }}

        .nav-link {{
            padding: 1rem 0;
            text-decoration: none;
            color: var(--gray-600);
            font-weight: 500;
            border-bottom: 3px solid transparent;
            transition: all 0.2s;
            white-space: nowrap;
        }}

        .nav-link:hover {{
            color: var(--primary);
            border-bottom-color: var(--primary);
        }}

        /* Main Content */
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 3rem 2rem;
        }}

        section {{
            margin-bottom: 5rem;
        }}

        h2 {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 2rem;
            color: var(--dark);
            display: flex;
            align-items: center;
            gap: 1rem;
        }}

        h2 i {{
            color: var(--primary);
            font-size: 1.5rem;
        }}

        h3 {{
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            color: var(--gray-700);
        }}

        /* Charts Section */
        .chart-container {{
            background: white;
            padding: 2rem;
            border-radius: 1rem;
            box-shadow: var(--shadow);
            margin-bottom: 3rem;
        }}

        .chart-title {{
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            color: var(--gray-700);
        }}

        .chart-image {{
            width: 100%;
            height: auto;
            border-radius: 0.5rem;
            box-shadow: var(--shadow);
        }}

        .chart-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 3rem;
        }}

        /* Framework Summary Cards */
        .framework-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }}

        .framework-card {{
            background: white;
            border-radius: 1rem;
            padding: 2rem;
            box-shadow: var(--shadow);
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .framework-card:hover {{
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
        }}

        .framework-name {{
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--primary);
        }}

        .framework-stats {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }}

        .framework-stat {{
            padding: 0.75rem;
            background: var(--gray-100);
            border-radius: 0.5rem;
        }}

        .framework-stat-label {{
            font-size: 0.75rem;
            color: var(--gray-600);
            margin-bottom: 0.25rem;
        }}

        .framework-stat-value {{
            font-size: 1rem;
            font-weight: 600;
            color: var(--dark);
        }}

        /* Per-File Breakdown Tables */
        .breakdown-section {{
            background: white;
            border-radius: 1rem;
            padding: 2rem;
            box-shadow: var(--shadow);
            margin-bottom: 2rem;
            overflow-x: auto;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.875rem;
        }}

        th {{
            background: var(--gray-100);
            padding: 1rem;
            text-align: left;
            font-weight: 600;
            color: var(--gray-700);
            position: sticky;
            top: 0;
            z-index: 10;
        }}

        td {{
            padding: 0.75rem 1rem;
            border-bottom: 1px solid var(--gray-200);
        }}

        tr:hover {{
            background: var(--gray-100);
        }}

        .status-success {{
            color: var(--success);
            font-weight: 500;
        }}

        .status-failed {{
            color: var(--danger);
            font-weight: 500;
        }}

        .status-timeout {{
            color: var(--warning);
            font-weight: 500;
        }}

        /* Responsive Design */
        @media (max-width: 768px) {{
            h1 {{
                font-size: 2rem;
            }}

            .header-stats {{
                grid-template-columns: 1fr;
            }}

            .framework-grid {{
                grid-template-columns: 1fr;
            }}

            .nav-content {{
                padding: 0 1rem;
            }}

            table {{
                font-size: 0.75rem;
            }}

            th, td {{
                padding: 0.5rem;
            }}
        }}

        /* Footer */
        footer {{
            background: var(--dark);
            color: white;
            padding: 3rem 0;
            margin-top: 5rem;
        }}

        .footer-content {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 2rem;
            text-align: center;
        }}

        .github-link {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: var(--primary);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            text-decoration: none;
            font-weight: 500;
            transition: background 0.2s;
            margin-top: 1rem;
        }}

        .github-link:hover {{
            background: var(--primary-dark);
        }}

        /* Smooth scrolling */
        html {{
            scroll-behavior: smooth;
        }}
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <h1>Python Text Extraction Libraries Benchmarks 2025</h1>
            <p class="subtitle">Comprehensive Performance Analysis of Text Extraction Frameworks</p>

            <div class="header-stats">
                <div class="stat-card">
                    <div class="stat-value">{len({s.framework for s in aggregated.summaries})}</div>
                    <div class="stat-label">Frameworks Tested</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{total_files:,}</div>
                    <div class="stat-label">Total Files Processed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{overall_success_rate:.1f}%</div>
                    <div class="stat-label">Overall Success Rate</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len({s.category for s in aggregated.summaries})}</div>
                    <div class="stat-label">Test Categories</div>
                </div>
            </div>
        </div>
    </header>

    <nav>
        <div class="nav-content">
            <a href="#overview" class="nav-link">Overview</a>
            <a href="#performance" class="nav-link">Performance</a>
            <a href="#memory" class="nav-link">Memory Usage</a>
            <a href="#success-rates" class="nav-link">Success Rates</a>
            <a href="#throughput" class="nav-link">Throughput</a>
            <a href="#file-breakdowns" class="nav-link">File Breakdowns</a>
            <a href="#category-analysis" class="nav-link">Category Analysis</a>
            <a href="#interactive" class="nav-link">Interactive Dashboard</a>
        </div>
    </nav>

    <div class="container">
        <section id="overview">
            <h2><i class="fas fa-chart-line"></i> Framework Overview</h2>

            <div class="framework-grid">
                {self._generate_framework_cards(framework_summary)}
            </div>
        </section>

        <section id="performance">
            <h2><i class="fas fa-tachometer-alt"></i> Performance Analysis</h2>

            <div class="chart-grid">
                <div class="chart-container">
                    <h3 class="chart-title">Average Extraction Time by Framework and Category</h3>
                    <img src="charts/performance_comparison_large.png" alt="Performance Comparison" class="chart-image">
                </div>

                <div class="chart-container">
                    <h3 class="chart-title">Performance by File Size Category</h3>
                    <img src="charts/performance_by_size_category.png" alt="Performance by Size" class="chart-image">
                </div>
            </div>
        </section>

        <section id="memory">
            <h2><i class="fas fa-memory"></i> Resource Usage</h2>

            <div class="chart-container">
                <h3 class="chart-title">Memory and CPU Usage Heatmaps</h3>
                <img src="charts/resource_usage_heatmaps.png" alt="Resource Usage" class="chart-image">
            </div>
        </section>

        <section id="success-rates">
            <h2><i class="fas fa-check-circle"></i> Success Rate Analysis</h2>

            <div class="chart-container">
                <h3 class="chart-title">Success Rates and Failure Analysis</h3>
                <img src="charts/success_and_failure_analysis.png" alt="Success Analysis" class="chart-image">
            </div>
        </section>

        <section id="throughput">
            <h2><i class="fas fa-rocket"></i> Throughput Performance</h2>

            <div class="chart-container">
                <h3 class="chart-title">Comprehensive Throughput Analysis</h3>
                <img src="charts/throughput_analysis_comprehensive.png" alt="Throughput Analysis" class="chart-image">
            </div>
        </section>

        <section id="file-breakdowns">
            <h2><i class="fas fa-file-alt"></i> Per-File Performance Breakdowns</h2>

            {self._generate_file_breakdown_sections(file_breakdowns)}
        </section>

        <section id="category-analysis">
            <h2><i class="fas fa-layer-group"></i> Category Analysis</h2>

            <div class="chart-container">
                <h3 class="chart-title">Comprehensive Category Performance Analysis</h3>
                <img src="charts/category_analysis_comprehensive.png" alt="Category Analysis" class="chart-image">
            </div>
        </section>

        <section id="interactive">
            <h2><i class="fas fa-chart-area"></i> Interactive Dashboard</h2>

            <div class="chart-container">
                <p>Explore the data interactively with our comprehensive dashboard:</p>
                <a href="charts/interactive_dashboard_enhanced.html" class="github-link" target="_blank">
                    <i class="fas fa-external-link-alt"></i> Open Interactive Dashboard
                </a>
            </div>
        </section>
    </div>

    <footer>
        <div class="footer-content">
            <p>Generated on {datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")}</p>
            <a href="https://github.com/Goldziher/python-text-extraction-libraries-benchmarks-2025" class="github-link">
                <i class="fab fa-github"></i> View on GitHub
            </a>
        </div>
    </footer>

    <script>
        // Smooth scroll offset for sticky nav
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                const navHeight = document.querySelector('nav').offsetHeight;
                const targetPosition = target.offsetTop - navHeight - 20;

                window.scrollTo({{
                    top: targetPosition,
                    behavior: 'smooth'
                }});
            }});
        }});

        // Active nav link highlighting
        const sections = document.querySelectorAll('section');
        const navLinks = document.querySelectorAll('.nav-link');

        window.addEventListener('scroll', () => {{
            let current = '';
            sections.forEach(section => {{
                const sectionTop = section.offsetTop;
                const sectionHeight = section.clientHeight;
                if (scrollY >= sectionTop - 200) {{
                    current = section.getAttribute('id');
                }}
            }});

            navLinks.forEach(link => {{
                link.style.borderBottomColor = 'transparent';
                link.style.color = 'var(--gray-600)';
                if (link.getAttribute('href').slice(1) === current) {{
                    link.style.borderBottomColor = 'var(--primary)';
                    link.style.color = 'var(--primary)';
                }}
            }});
        }});
    </script>
</body>
</html>
"""

    def _get_framework_summary(self, aggregated: AggregatedResults) -> dict[str, dict[str, Any]]:
        """Calculate framework summary statistics."""
        summary = {}

        for result in aggregated.summaries:
            fw = result.framework
            if fw not in summary:
                summary[fw] = {
                    "total_files": 0,
                    "successful": 0,
                    "failed": 0,
                    "avg_times": [],
                    "avg_memory": [],
                    "throughputs": [],
                }

            summary[fw]["total_files"] += result.total_files
            summary[fw]["successful"] += result.successful_files
            summary[fw]["failed"] += result.failed_files + result.timeout_files

            if result.avg_extraction_time:
                summary[fw]["avg_times"].append(result.avg_extraction_time)
            if result.avg_peak_memory_mb:
                summary[fw]["avg_memory"].append(result.avg_peak_memory_mb)
            if result.mb_per_second:
                summary[fw]["throughputs"].append(result.mb_per_second)

        # Calculate averages
        for data in summary.values():
            data["avg_time"] = sum(data["avg_times"]) / len(data["avg_times"]) if data["avg_times"] else 0
            data["avg_memory_mb"] = sum(data["avg_memory"]) / len(data["avg_memory"]) if data["avg_memory"] else 0
            data["avg_throughput"] = sum(data["throughputs"]) / len(data["throughputs"]) if data["throughputs"] else 0
            data["success_rate"] = (data["successful"] / data["total_files"] * 100) if data["total_files"] > 0 else 0

        return summary

    def _generate_framework_cards(self, summary: dict[str, dict[str, Any]]) -> str:
        """Generate HTML for framework summary cards."""
        html = ""

        for fw, data in sorted(summary.items()):
            html += f"""
            <div class="framework-card">
                <div class="framework-name">{fw}</div>
                <div class="framework-stats">
                    <div class="framework-stat">
                        <div class="framework-stat-label">Success Rate</div>
                        <div class="framework-stat-value">{data["success_rate"]:.1f}%</div>
                    </div>
                    <div class="framework-stat">
                        <div class="framework-stat-label">Avg Time</div>
                        <div class="framework-stat-value">{data["avg_time"]:.3f}s</div>
                    </div>
                    <div class="framework-stat">
                        <div class="framework-stat-label">Avg Memory</div>
                        <div class="framework-stat-value">{data["avg_memory_mb"]:.0f} MB</div>
                    </div>
                    <div class="framework-stat">
                        <div class="framework-stat-label">Throughput</div>
                        <div class="framework-stat-value">{data["avg_throughput"]:.1f} MB/s</div>
                    </div>
                </div>
            </div>
            """

        return html

    def _get_file_breakdowns(self, aggregated: AggregatedResults) -> dict[str, list[dict[str, Any]]]:
        """Get per-file performance breakdowns by category."""
        breakdowns = {}

        for result in aggregated.results:
            category = result.metadata.category
            if category not in breakdowns:
                breakdowns[category] = []

            breakdowns[category].append(
                {
                    "framework": result.metadata.framework,
                    "file": Path(result.metadata.file_path).name,
                    "size_mb": result.metadata.file_size_bytes / (1024 * 1024),
                    "time": result.metrics.extraction_time,
                    "memory_mb": result.metrics.peak_memory_mb or 0,
                    "cpu_percent": result.metrics.avg_cpu_percent or 0,
                    "status": result.metadata.status,
                    "error": result.metadata.error_message,
                }
            )

        return breakdowns

    def _generate_file_breakdown_sections(self, breakdowns: dict[str, list[dict[str, Any]]]) -> str:
        """Generate HTML for file breakdown tables."""
        html = ""

        # Focus on key categories
        key_categories = ["tiny", "small", "medium", "large", "huge"]

        for category in key_categories:
            if category not in breakdowns:
                continue

            data = breakdowns[category]

            # Sort by file name for consistent ordering
            data.sort(key=lambda x: (x["file"], x["framework"]))

            html += f"""
            <div class="breakdown-section">
                <h3>{category.title()} Files - Detailed Performance</h3>
                <table>
                    <thead>
                        <tr>
                            <th>File</th>
                            <th>Size (MB)</th>
                            <th>Framework</th>
                            <th>Time (s)</th>
                            <th>Memory (MB)</th>
                            <th>CPU (%)</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
            """

            for item in data:
                status_class = f"status-{item['status']}"
                status_text = item["status"].title()
                if item["error"]:
                    status_text += f" ({item['error'][:50]}...)"

                html += f"""
                        <tr>
                            <td>{item["file"]}</td>
                            <td>{item["size_mb"]:.2f}</td>
                            <td>{item["framework"]}</td>
                            <td>{item["time"]:.3f}</td>
                            <td>{item["memory_mb"]:.0f}</td>
                            <td>{item["cpu_percent"]:.1f}</td>
                            <td class="{status_class}">{status_text}</td>
                        </tr>
                """

            html += """
                    </tbody>
                </table>
            </div>
            """

        # Also add a summary table showing best performers per file
        html += self._generate_best_performers_table(breakdowns)

        return html

    def _generate_best_performers_table(self, breakdowns: dict[str, list[dict[str, Any]]]) -> str:
        """Generate a table showing the best performing framework for each file."""
        html = """
        <div class="breakdown-section">
            <h3>Best Performing Framework by File</h3>
            <table>
                <thead>
                    <tr>
                        <th>Category</th>
                        <th>File</th>
                        <th>Best Framework</th>
                        <th>Time (s)</th>
                        <th>Runner-up</th>
                        <th>Runner-up Time (s)</th>
                        <th>Speed Advantage</th>
                    </tr>
                </thead>
                <tbody>
        """

        for category in ["tiny", "small", "medium", "large", "huge"]:
            if category not in breakdowns:
                continue

            # Group by file
            files = {}
            for item in breakdowns[category]:
                if item["status"] == "success":
                    file = item["file"]
                    if file not in files:
                        files[file] = []
                    files[file].append(item)

            # Find best performers
            for file, results in files.items():
                if len(results) < 2:
                    continue

                sorted_results = sorted(results, key=lambda x: x["time"])
                best = sorted_results[0]
                runner_up = sorted_results[1]

                speed_advantage = (runner_up["time"] - best["time"]) / runner_up["time"] * 100

                html += f"""
                    <tr>
                        <td>{category.title()}</td>
                        <td>{file}</td>
                        <td style="font-weight: 600; color: var(--success)">{best["framework"]}</td>
                        <td>{best["time"]:.3f}</td>
                        <td>{runner_up["framework"]}</td>
                        <td>{runner_up["time"]:.3f}</td>
                        <td>{speed_advantage:.1f}% faster</td>
                    </tr>
                """

        html += """
                </tbody>
            </table>
        </div>
        """

        return html
