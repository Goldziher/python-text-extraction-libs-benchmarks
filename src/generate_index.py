"""Generate dynamic HTML index for GitHub Pages from aggregated results."""

import re
from pathlib import Path

import msgspec


def get_framework_versions() -> dict[str, str]:
    """Extract framework versions from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        pyproject_path = Path("../pyproject.toml")

    if pyproject_path.exists():
        # Parse pyproject.toml manually to avoid tomllib import issues
        with open(pyproject_path) as f:
            content = f.read()

        # Extract dependencies section
        deps_match = re.search(r"dependencies\s*=\s*\[(.*?)\]", content, re.DOTALL)
        if deps_match:
            deps_text = deps_match.group(1)
            deps = [line.strip().strip('"').strip("'") for line in deps_text.split(",") if line.strip()]

            versions = {}
            for dep in deps:
                if "kreuzberg>=" in dep:
                    versions["kreuzberg"] = dep.split(">=")[1]
                elif "docling>=" in dep:
                    versions["docling"] = dep.split(">=")[1]
                elif "markitdown>=" in dep:
                    versions["markitdown"] = dep.split(">=")[1]
                elif "unstructured" in dep and ">=" in dep:
                    versions["unstructured"] = dep.split(">=")[1].split("[")[0]
                elif "extractous>=" in dep:
                    versions["extractous"] = dep.split(">=")[1]

            return versions

    # Fallback versions
    return {
        "kreuzberg": "4.0.0rc1",
        "docling": "2.41.0",
        "markitdown": "0.0.1a2",
        "unstructured": "0.18.5",
        "extractous": "0.1.0",
    }


def generate_index_html(aggregated_path: Path, output_path: Path) -> None:
    """Generate index.html from aggregated results."""
    # Load aggregated results
    with open(aggregated_path, "rb") as f:
        results = msgspec.json.decode(f.read())

    # Get framework versions
    versions = get_framework_versions()

    # Calculate metrics for the summary table
    framework_stats = {}

    for framework, summaries in results["framework_summaries"].items():
        if not summaries:
            continue

        # Calculate overall metrics
        total_files = sum(s["total_files"] for s in summaries)
        successful_files = sum(s["successful_files"] for s in summaries)

        # Success rate on files actually tested
        success_rate = (successful_files / total_files * 100) if total_files > 0 else 0

        # Average speed (files per second)
        speeds = [s["files_per_second"] for s in summaries if s.get("files_per_second")]
        avg_speed = sum(speeds) / len(speeds) if speeds else 0

        # Average memory usage
        memories = [s["avg_peak_memory_mb"] for s in summaries if s.get("avg_peak_memory_mb")]
        avg_memory = sum(memories) / len(memories) if memories else 0

        framework_stats[framework] = {
            "success_rate": success_rate,
            "avg_speed": avg_speed,
            "avg_memory": avg_memory,
            "total_files": total_files,
            "successful_files": successful_files,
        }

    # Generate HTML with CSS template
    css_styles = """
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        .header { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 30px; text-align: center; }
        .logo { height: 60px; margin-bottom: 20px; }
        h1 { margin: 0 0 10px 0; font-size: 2.5em; }
        .subtitle { color: #666; font-size: 1.2em; }
        .nav { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 30px; text-align: center; }
        .nav a { margin: 0 15px; text-decoration: none; color: #007bff; font-weight: 500; }
        .nav a:hover { text-decoration: underline; }
        .section { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 30px; }
        h2 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; margin-bottom: 20px; }
        .alert { padding: 15px; background: #e3f2fd; border-left: 4px solid #2196f3; margin-bottom: 20px; border-radius: 5px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; font-weight: 600; color: #2c3e50; }
        tr:hover { background: #f8f9fa; }
        .framework-card { border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 20px; background: #fafafa; }
        .framework-card h4 { margin-top: 0; color: #2c3e50; }
        .chart-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin: 20px 0; }
        .chart-item { text-align: center; }
        .chart-item img { max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .footer { text-align: center; color: #666; margin-top: 50px; padding: 20px; }
        .footer a { color: #007bff; text-decoration: none; }
        small { color: #666; font-style: italic; }
    """

    # Generate HTML
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python Text Extraction Libraries Benchmark Results</title>
    <link rel="icon" type="image/png" href="assets/favicon.png">
    <style>
{css_styles}
    </style>
</head>
<body>
    <div class="header">
        <img src="assets/logo.png" alt="Kreuzberg Logo" class="logo">
        <h1>📊 Python Text Extraction Libraries Benchmark Results</h1>
        <p class="subtitle">Comprehensive Performance Analysis of Text Extraction Frameworks</p>
    </div>

    <nav class="nav">
        <a href="#summary">Executive Summary</a>
        <a href="#performance">Performance</a>
        <a href="#resources">Resource Usage</a>
        <a href="#formats">Format Support</a>
        <a href="#frameworks">Frameworks</a>
        <a href="#reports">Reports</a>
    </nav>

    <section id="summary" class="section">
        <h2>🎯 Executive Summary</h2>

        <div class="alert">
            <strong>Latest Benchmark Run:</strong> Testing ALL 18 formats for comprehensive framework assessment
        </div>

        <h3>Framework Performance Rankings</h3>
        <table>
            <thead>
                <tr>
                    <th>Framework</th>
                    <th>Avg Speed (files/sec)</th>
                    <th>Success Rate</th>
                    <th>Memory Usage (MB)</th>
                    <th>Installation Size</th>
                </tr>
            </thead>
            <tbody>"""

    # Sort frameworks by speed
    sorted_frameworks = sorted(framework_stats.items(), key=lambda x: x[1]["avg_speed"], reverse=True)

    # Installation sizes (hardcoded for now, could be dynamic)
    install_sizes = {
        "kreuzberg_sync": "71MB",
        "kreuzberg_async": "71MB",
        "docling": "1GB+",
        "markitdown": "251MB",
        "unstructured": "146MB",
        "extractous": "~100MB",
    }

    for fw_name, stats in sorted_frameworks:
        html += f"""
                <tr>
                    <td>{fw_name.replace("_", " ").title()}</td>
                    <td>{stats["avg_speed"]:.2f}</td>
                    <td>{stats["success_rate"]:.1f}%</td>
                    <td>{stats["avg_memory"]:.1f}</td>
                    <td>{install_sizes.get(fw_name, "N/A")}</td>
                </tr>"""

    html += """
            </tbody>
        </table>
        <p><small>Success rates calculated on files actually tested by each framework</small></p>
    </section>

    <section id="performance" class="section">
        <h2>📊 Performance Analysis</h2>

        <div class="chart-grid">
            <div class="chart-item">
                <h3>Extraction Speed Comparison</h3>
                <img src="visualizations/performance_comparison.png" alt="Performance Comparison">
            </div>
            <div class="chart-item">
                <h3>Throughput Analysis</h3>
                <img src="visualizations/throughput_comparison.png" alt="Throughput Comparison">
            </div>
            <div class="chart-item">
                <h3>Success Rate Analysis</h3>
                <img src="visualizations/success_rate_comparison.png" alt="Success Rate Comparison">
            </div>
            <div class="chart-item">
                <h3>Performance Heatmap</h3>
                <img src="visualizations/performance_heatmap.png" alt="Performance Heatmap">
            </div>
        </div>

        <p style="text-align: center; margin-top: 20px;">
            <a href="visualizations/interactive_dashboard.html" style="background: #007bff; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none;">
                📈 Open Interactive Dashboard
            </a>
        </p>
    </section>

    <section id="resources" class="section">
        <h2>💾 Resource Usage Analysis</h2>

        <div class="chart-grid">
            <div class="chart-item">
                <h3>Memory Usage by Framework</h3>
                <img src="visualizations/memory_usage.png" alt="Memory Usage">
            </div>
            <div class="chart-item">
                <h3>Category Performance</h3>
                <img src="visualizations/category_analysis.png" alt="Category Analysis">
            </div>
            <div class="chart-item">
                <h3>Installation Size Comparison</h3>
                <img src="visualizations/installation_sizes.png" alt="Installation Sizes">
            </div>
            <div class="chart-item">
                <h3>Data Throughput</h3>
                <img src="visualizations/data_throughput.png" alt="Data Throughput">
            </div>
        </div>
    </section>

    <section id="formats" class="section">
        <h2>📄 Format Support Analysis</h2>

        <div class="chart-grid">
            <div class="chart-item">
                <h3>Format Support Matrix</h3>
                <img src="visualizations/format_support_matrix.png" alt="Format Support Matrix">
            </div>
            <div class="chart-item">
                <h3>Quality Assessment</h3>
                <img src="visualizations/quality_assessment.png" alt="Quality Assessment">
            </div>
        </div>

        <h3>Format Categories Tested</h3>
        <ul>
            <li><strong>Documents:</strong> PDF, DOCX, PPTX, XLSX, XLS, ODT</li>
            <li><strong>Web/Markup:</strong> HTML, MD, RST, ORG</li>
            <li><strong>Images:</strong> PNG, JPG, JPEG, BMP</li>
            <li><strong>Email:</strong> EML, MSG</li>
            <li><strong>Data:</strong> CSV, JSON, YAML</li>
            <li><strong>Text:</strong> TXT</li>
        </ul>

        <h3>Framework Exclusions</h3>
        <ul>
            <li><strong>Kreuzberg:</strong> Email formats (EML, MSG) and data formats (JSON, YAML) only</li>
            <li><strong>Extractous:</strong> Skips DOCX, JPG</li>
            <li><strong>Docling:</strong> Limited format support</li>
            <li><strong>MarkItDown:</strong> Skips DOCX, MD, ODT</li>
            <li><strong>Unstructured:</strong> Skips JPEG, JPG, ODT, ORG, RST</li>
        </ul>
    </section>

    <section id="frameworks" class="section">
        <h2>🔧 Framework Details</h2>

        <div class="framework-card">
            <h4>Kreuzberg</h4>
            <p><strong>Version:</strong> {kreuzberg_version} | <strong>Size:</strong> 71MB base</p>
            <p>Fast Python text extraction with multiple OCR backends. Supports both sync and async APIs.</p>
            <p><strong>Strengths:</strong> Speed, small footprint, async support</p>
            <p><strong>Limitations:</strong> No email/data format support (by design)</p>
        </div>

        <div class="framework-card">
            <h4>Docling</h4>
            <p><strong>Version:</strong> {docling_version} | <strong>Size:</strong> 1GB+</p>
            <p>IBM Research's advanced document understanding with ML models.</p>
            <p><strong>Strengths:</strong> Advanced ML understanding, high quality</p>
            <p><strong>Limitations:</strong> Large size, slower on complex PDFs</p>
        </div>

        <div class="framework-card">
            <h4>MarkItDown</h4>
            <p><strong>Version:</strong> {markitdown_version} | <strong>Size:</strong> 251MB</p>
            <p>Microsoft's lightweight Markdown converter optimized for LLM processing.</p>
            <p><strong>Strengths:</strong> LLM-optimized output, ONNX performance</p>
            <p><strong>Limitations:</strong> Limited format support</p>
        </div>

        <div class="framework-card">
            <h4>Unstructured</h4>
            <p><strong>Version:</strong> {unstructured_version} | <strong>Size:</strong> 146MB</p>
            <p>Enterprise solution supporting 64+ file types.</p>
            <p><strong>Strengths:</strong> Widest format support, enterprise features</p>
            <p><strong>Limitations:</strong> Moderate speed</p>
        </div>

        <div class="framework-card">
            <h4>Extractous</h4>
            <p><strong>Version:</strong> {extractous_version} | <strong>Size:</strong> ~100MB</p>
            <p>Fast Rust-based extraction with Python bindings.</p>
            <p><strong>Strengths:</strong> Native performance, low memory usage</p>
            <p><strong>Limitations:</strong> Newer library, some format gaps</p>
        </div>
    </section>

    <section id="reports" class="section">
        <h2>📋 Detailed Reports & Data</h2>

        <p>
            <a href="reports/benchmark_report.html">🌐 HTML Report</a> |
            <a href="reports/benchmark_report.md">📝 Markdown Report</a> |
            <a href="reports/benchmark_metrics.json">📊 JSON Metrics</a> |
            <a href="visualizations/summary_metrics.json">📊 Summary Data</a>
        </p>

        <h3>🔬 Advanced Analysis</h3>
        <p>
            <a href="visualizations/file-type-analysis/interactive_dashboard.html" style="background: #28a745; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; margin-right: 10px;">
                📊 File Type Performance Dashboard
            </a>
            <a href="visualizations/file-type-analysis/performance_insights.md" style="background: #17a2b8; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none;">📝 Per-Format Analysis</a>
        </p>

        <h3>🎯 Key Insights from File Type Analysis</h3>
        <ul>
            <li><strong>Extractous</strong> dominates data formats (JSON/YAML) with 100% success rates</li>
            <li><strong>Kreuzberg Sync</strong> achieves extreme speeds on spreadsheets (1800+ files/sec)</li>
            <li><strong>Framework specializations</strong> clearly visible across different file types</li>
            <li><strong>Interactive filtering</strong> available by framework and file category</li>
        </ul>

        <h3>Links</h3>
        <ul>
            <li><a href="https://github.com/Goldziher/python-text-extraction-libs-benchmarks">📂 GitHub Repository</a></li>
            <li><a href="https://github.com/Goldziher/python-text-extraction-libs-benchmarks/actions">⚙️ GitHub Actions</a></li>
        </ul>
    </section>

    <div class="footer">
        <p>Powered by <a href="https://github.com/Kreuzberg">Kreuzberg</a> • Comprehensive text extraction benchmarking</p>
        <p>Updated regularly via GitHub Actions • CPU-only processing • Python 3.13+</p>
    </div>
</body>
</html>"""

    # Format the HTML with versions and CSS
    html = html.format(
        css_styles=css_styles,
        kreuzberg_version=versions.get("kreuzberg", "3.7.0"),
        docling_version=versions.get("docling", "2.41.0"),
        markitdown_version=versions.get("markitdown", "0.0.1a2"),
        unstructured_version=versions.get("unstructured", "0.18.5"),
        extractous_version=versions.get("extractous", "0.1.0"),
    )

    # Save the HTML
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html)
    print(f"Generated index.html at {output_path}")


def main():
    """Main function for command line usage."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python generate_index.py <aggregated_results.json> [output_path]")
        sys.exit(1)

    aggregated_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("index.html")

    generate_index_html(aggregated_path, output_path)


if __name__ == "__main__":
    main()
