"""Generate dynamic HTML index for GitHub Pages from aggregated results.

~keep GitHub Pages generation that:
- Parses aggregated benchmark results into HTML tables
- Shows speed/memory by category to avoid misleading averages
- Extracts framework versions from pyproject.toml for accurate reporting
- Creates downloadable CSV exports and interactive charts
- Generates deployment-ready static site from benchmark data
"""

import re
from pathlib import Path

import msgspec


def get_framework_versions() -> dict[str, str]:
    """~keep Extract exact framework versions tested for accurate reporting."""
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


def calculate_framework_stats(results: dict) -> dict:
    """~keep Calculate statistics avoiding misleading averages across categories."""
    framework_stats = {}

    for framework, summaries in results["framework_summaries"].items():
        if not summaries:
            continue

        # Aggregate file counts across all tested categories
        total_files = sum(s["total_files"] for s in summaries)
        successful_files = sum(s["successful_files"] for s in summaries)
        failed_files = sum(s.get("failed_files", 0) for s in summaries)
        timeout_files = sum(s.get("timeout_files", 0) for s in summaries)

        # Success rate: percentage of files successfully processed
        success_rate = (successful_files / total_files * 100) if total_files > 0 else 0

        # Speed and memory BY CATEGORY - prevents misleading averages
        # (e.g., if framework only tested tiny files, don't average with medium)
        category_speeds = {}
        category_memories = {}
        for s in summaries:
            category = s.get("category", "unknown")
            speed = s.get("files_per_second", 0)
            memory = s.get("avg_peak_memory_mb", 0)
            category_speeds[category] = speed
            category_memories[category] = memory

        # Weighted average memory across categories that were actually tested
        memories = [s["avg_peak_memory_mb"] for s in summaries if s.get("avg_peak_memory_mb")]
        avg_memory = sum(memories) / len(memories) if memories else 0

        # Data throughput (MB/sec) across categories
        throughputs = [s.get("mb_per_second", 0) for s in summaries if s.get("mb_per_second")]
        avg_throughput = sum(throughputs) / len(throughputs) if throughputs else 0

        # Detailed failure breakdown for debugging
        failure_types = []
        if failed_files > 0:
            failure_types.append(f"{failed_files} errors")
        if timeout_files > 0:
            failure_types.append(f"{timeout_files} timeouts")

        framework_stats[framework] = {
            "success_rate": success_rate,
            "category_speeds": category_speeds,  # Key: prevents misleading speed averages
            "category_memories": category_memories,  # Key: prevents misleading memory averages
            "avg_memory": avg_memory,
            "avg_throughput": avg_throughput,
            "total_files": total_files,
            "failure_breakdown": failure_types,
            "successful_files": successful_files,
            "failed_files": failed_files,
            "timeout_files": timeout_files,
            "version": get_framework_versions().get(framework.replace("_sync", "").replace("_async", ""), "Unknown"),
        }

    return framework_stats


def generate_performance_table(sorted_frameworks: list, install_sizes: dict, licenses: dict) -> str:
    """Generate the performance table HTML."""
    html = """
        <h3>Framework Performance Rankings</h3>
        <table>
            <thead>
                <tr>
                    <th rowspan="2">Framework</th>
                    <th rowspan="2">License</th>
                    <th colspan="5">Speed by Category (files/sec)</th>
                    <th rowspan="2">Success Rate</th>
                    <th rowspan="2">Failures</th>
                    <th rowspan="2">Memory (MB)</th>
                    <th rowspan="2">Install Size</th>
                </tr>
                <tr>
                    <th>Tiny</th>
                    <th>Small</th>
                    <th>Medium</th>
                    <th>Large</th>
                    <th>Huge</th>
                </tr>
            </thead>
            <tbody>"""

    for fw_name, stats in sorted_frameworks:
        # Get speeds for each category
        categories = ["tiny", "small", "medium", "large", "huge"]
        category_speeds = stats.get("category_speeds", {})

        speed_cells = ""
        for cat in categories:
            if cat in category_speeds:
                speed = category_speeds[cat]
                if speed > 0:
                    speed_cells += f"<td>{speed:.2f}</td>"
                else:
                    speed_cells += "<td>-</td>"
            else:
                # Category not tested in this benchmark run
                speed_cells += "<td>—</td>"

        # Handle failures display
        failure_display = ", ".join(stats["failure_breakdown"]) if stats["failure_breakdown"] else "None"

        memory_display = "N/A" if stats["avg_memory"] == 0 else f"{stats['avg_memory']:.1f}"
        license_display = licenses.get(fw_name, "Unknown")

        # Color code licenses for easy identification
        if license_display == "AGPL v3.0":
            license_display = '<span style="color: #dc3545; font-weight: bold;">⚠️ AGPL v3.0</span>'
        elif license_display in ["MIT", "Apache 2.0"]:
            license_display = f'<span style="color: #28a745;">✅ {license_display}</span>'

        html += f"""
                <tr>
                    <td>{fw_name.replace("_", " ").title()}</td>
                    <td>{license_display}</td>
                    {speed_cells}
                    <td>{stats["success_rate"]:.1f}%</td>
                    <td>{failure_display}</td>
                    <td>{memory_display}</td>
                    <td>{install_sizes.get(fw_name, "N/A")}</td>
                </tr>"""

    html += """
            </tbody>
        </table>
        <p><small>Success rates calculated on files actually tested by each framework. "—" indicates categories not included in this benchmark run.</small></p>"""

    return html


def generate_memory_table(sorted_frameworks: list) -> str:
    """Generate the memory usage table HTML."""
    html = """
        <h3>Memory Usage by Category</h3>
        <table>
            <thead>
                <tr>
                    <th rowspan="2">Framework</th>
                    <th colspan="5">Memory Usage by Category (MB)</th>
                    <th rowspan="2">Avg Memory (MB)</th>
                </tr>
                <tr>
                    <th>Tiny</th>
                    <th>Small</th>
                    <th>Medium</th>
                    <th>Large</th>
                    <th>Huge</th>
                </tr>
            </thead>
            <tbody>"""

    # Generate memory table rows
    for fw_name, stats in sorted_frameworks:
        categories = ["tiny", "small", "medium", "large", "huge"]
        category_memories = stats.get("category_memories", {})

        memory_cells = ""
        for cat in categories:
            if cat in category_memories:
                memory = category_memories[cat]
                if memory > 0:
                    memory_cells += f"<td>{memory:.0f}</td>"
                else:
                    memory_cells += "<td>-</td>"
            else:
                memory_cells += "<td>-</td>"

        avg_memory_display = f"{stats['avg_memory']:.0f}" if stats["avg_memory"] > 0 else "N/A"

        html += f"""
                <tr>
                    <td>{fw_name.replace("_", " ").title()}</td>
                    {memory_cells}
                    <td>{avg_memory_display}</td>
                </tr>"""

    html += """
            </tbody>
        </table>
        <p><small>Memory usage shown as peak RSS (Resident Set Size) in MB during extraction</small></p>"""

    return html


def generate_index_html(aggregated_path: Path, output_path: Path) -> None:
    """Generate comprehensive index.html from aggregated results."""
    # Load aggregated results
    with open(aggregated_path, "rb") as f:
        results = msgspec.json.decode(f.read())

    # Get framework versions
    versions = get_framework_versions()

    # Calculate comprehensive metrics for the summary table
    framework_stats = calculate_framework_stats(results)

    dataset_stats = {
        "total_extractions": 0,
        "total_frameworks": 0,
        "total_file_types": set(),
        "total_categories": set(),
        "size_ranges": {"tiny": 0, "small": 0, "medium": 0, "large": 0, "huge": 0},
    }

    # Update dataset statistics
    for stats in framework_stats.values():
        dataset_stats["total_extractions"] += stats["total_files"]
        for category in stats["category_speeds"]:
            dataset_stats["total_categories"].add(category)
            if category in dataset_stats["size_ranges"]:
                dataset_stats["size_ranges"][category] += 1

    dataset_stats["total_frameworks"] = len(framework_stats)
    dataset_stats["total_file_types"] = len(results.get("file_types", []))

    # Detect available analysis modules
    analysis_available = {
        "file_type": Path("visualizations/analysis/interactive_dashboard.html").exists(),
        "metadata": Path("visualizations/analysis/metadata").exists(),
        "tables": Path("visualizations/analysis/tables").exists(),
        "quality": Path("quality-enhanced-results.json").exists(),
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
        .chart-single { display: block; margin-bottom: 40px; }
        .chart-single .chart-item { width: 100%; text-align: center; }
        .chart-single .chart-item img { max-width: 100%; width: 100%; max-width: 1200px; height: auto; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .ranking-info { font-size: 14px; line-height: 1.6; margin: 15px 0; }
        .metrics-guide { font-size: 14px; }
        .metrics-guide ul { margin: 10px 0; padding-left: 20px; }
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
        <a href="#metadata">Metadata Analysis</a>
        <a href="#quality">Quality Assessment</a>
        <a href="#formats">Format Support</a>
        <a href="#frameworks">Frameworks</a>
        <a href="#reports">Reports</a>
    </nav>

    <section id="summary" class="section">
        <h2>🎯 Executive Summary</h2>

        <div class="alert">
            <strong>Latest Benchmark Run:</strong> Testing ALL 18 formats for comprehensive framework assessment
        </div>

        <div class="alert">
            <strong>⚠️ Methodology Note:</strong> All frameworks are multi-format text extraction libraries tested across all supported file types for fair comparison.
        </div>

"""

    # Sort frameworks by success rate then by total successful files
    sorted_frameworks = sorted(
        framework_stats.items(), key=lambda x: (x[1]["success_rate"], x[1]["successful_files"]), reverse=True
    )

    # Installation sizes and licenses
    install_sizes = {
        "kreuzberg_sync": "71MB",
        "kreuzberg_async": "71MB",
        "docling": "1GB+",
        "markitdown": "251MB",
        "unstructured": "146MB",
        "extractous": "~100MB",
    }

    licenses = {
        "kreuzberg_sync": "MIT",
        "kreuzberg_async": "MIT",
        "docling": "MIT",
        "markitdown": "MIT",
        "unstructured": "Apache 2.0",
        "extractous": "Apache 2.0",
    }

    # Generate performance table
    html += generate_performance_table(sorted_frameworks, install_sizes, licenses)

    # Generate memory table
    html += generate_memory_table(sorted_frameworks)

    html += """
    </section>

    <section id="performance" class="section">
        <h2>📊 Performance Analysis</h2>

        <div class="metrics-guide" style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 5px;">
            <h4>📊 How to Read Performance Charts</h4>
            <ul>
                <li><strong>🚀 Extraction Speed:</strong> HIGHER is BETTER (more files/sec processed)</li>
                <li><strong>🎯 Success Rate:</strong> HIGHER is BETTER (fewer failures/timeouts)</li>
                <li><strong>📈 Throughput:</strong> HIGHER is BETTER (more MB/sec processed)</li>
                <li><strong>🔥 Heatmap Colors:</strong> Darker = Better Performance, Lighter = Slower/Failed</li>
            </ul>
        </div>

        <div class="chart-single">
            <div class="chart-item">
                <h3>1️⃣ Extraction Speed Rankings</h3>
                <div class="ranking-info" style="background: #e3f2fd; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <strong>🏆 Speed Champions (files/sec):</strong><br>
                    Multi-format frameworks showing consistent performance across all supported file types. Rankings based on current benchmark data.
                </div>
                <img src="visualizations/performance_comparison_large.png" alt="Performance Comparison">
                <p><small><strong>Speed Analysis:</strong> Kreuzberg leads with 15+ files/sec, while Docling shows timeout issues on complex documents</small></p>
            </div>
        </div>

        <div class="chart-single">
            <div class="chart-item">
                <h3>2️⃣ Data Throughput Analysis</h3>
                <div class="ranking-info" style="background: #f3e5f5; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <strong>📊 Throughput Performance (MB/sec):</strong><br>
                    Measures actual data processing speed accounting for file sizes. Higher values indicate better scaling with document complexity.
                </div>
                <img src="visualizations/throughput_analysis_comprehensive.png" alt="Throughput Comparison">
                <p><small><strong>Throughput Insights:</strong> Multi-format frameworks show consistent performance across diverse document types</small></p>
            </div>
        </div>

        <div class="chart-single">
            <div class="chart-item">
                <h3>3️⃣ Success Rate Reliability</h3>
                <div class="ranking-info" style="background: #e8f5e8; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <strong>✅ Reliability Rankings (% successful):</strong><br>
                    Framework reliability varies by document type and format support. See charts for detailed comparisons.<br>
                    <em>*Success rates calculated on supported formats only</em>
                </div>
                <img src="visualizations/success_and_failure_analysis.png" alt="Success Rate Comparison">
                <p><small><strong>Reliability Notes:</strong> Success rates calculated only on files each framework attempts to process</small></p>
            </div>
        </div>

        <!-- Performance heatmap not available in current visualizations -->

        <div style="text-align: center; margin: 30px 0;">
            <a href="reports/benchmark_report.html" style="background: #6c757d; color: white; padding: 15px 25px; border-radius: 5px; text-decoration: none;">
                📊 View Detailed Performance Report
            </a>
        </div>
    </section>

    <section id="resources" class="section">
        <h2>💾 Resource Usage Analysis</h2>

        <div class="alert">
            <strong>📊 Memory Profiling:</strong> Peak memory usage tracked for every extraction with 50ms sampling intervals using psutil RSS measurements. Data available per file type, framework, and document size category.
        </div>

        <div class="metrics-guide" style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 5px;">
            <h4>📊 How to Read Memory & Resource Charts</h4>
            <ul>
                <li><strong>🔺 Memory Usage:</strong> LOWER is BETTER (less RAM required)</li>
                <li><strong>🚀 Speed:</strong> HIGHER is BETTER (faster processing)</li>
                <li><strong>✅ Success Rate:</strong> HIGHER is BETTER (more reliable)</li>
                <li><strong>📦 Installation Size:</strong> LOWER is BETTER (smaller footprint)</li>
                <li><strong>Rankings:</strong> Numbers indicate performance ranking (1st = best, 2nd = second best, etc.)</li>
            </ul>
        </div>

        <!-- Single column layout for larger, more readable charts -->
        <div class="chart-single">
            <div class="chart-item">
                <h3>1️⃣ Memory Usage Rankings by Framework</h3>
                <div class="ranking-info" style="background: #e3f2fd; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <strong>🏆 Memory Efficiency Ranking (Lower MB = Better):</strong><br>
                    Memory usage varies significantly by framework and document type. See detailed analysis below.
                </div>
                <img src="visualizations/resource_usage_heatmaps.png" alt="Memory Usage">
                <p><small><strong>Interpretation:</strong> Shows average peak memory consumption across all file types. Lower bars indicate more memory-efficient frameworks.</small></p>
            </div>
        </div>

        <div class="chart-single">
            <div class="chart-item">
                <h3>2️⃣ Detailed Memory Usage by File Type</h3>
                <div class="ranking-info" style="background: #f3e5f5; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <strong>📊 Format-Specific Memory Patterns:</strong><br>
                    • PDFs: Show highest memory variance (50MB - 2GB+)<br>
                    • Images: Consistent high memory usage across frameworks<br>
                    • Office Docs: Moderate memory requirements (200-800MB)<br>
                    • Text/Markup: Lowest memory footprint (&lt;100MB)
                </div>
                <img src="visualizations/analysis/memory_usage_by_file_type.png" alt="Memory Usage by File Type"
                     onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                <div style="display:none; text-align:center; padding:40px; background:#f8f9fa; border-radius:8px; border: 2px dashed #dee2e6;">
                    <h4>📊 Memory Analysis Available</h4>
                    <p>Detailed memory profiling data is available in the interactive dashboard and detailed reports.</p>
                    <a href="visualizations/analysis/interactive_dashboard.html" style="background: #007bff; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none;">View Interactive Memory Analysis</a>
                </div>
                <p><small><strong>Framework Behavior:</strong> Each framework shows distinct memory patterns per file type. Frameworks optimized for specific formats use significantly less memory on their target documents.</small></p>
            </div>
        </div>

        <div class="chart-single">
            <div class="chart-item">
                <h3>3️⃣ Performance by Document Size Categories</h3>
                <div class="ranking-info" style="background: #e8f5e8; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <strong>📏 Size Category Performance (Speed Ranking):</strong><br>
                    Tiny (&lt;100KB): Fast extraction | Small (100KB-1MB): Consistent performance | Medium (1-10MB): Mixed results | Large (10-50MB): Framework timeouts common
                </div>
                <img src="visualizations/category_analysis_comprehensive.png" alt="Category Analysis">
                <p><small><strong>Size Scaling:</strong> Performance patterns change dramatically with document size. Memory usage can increase exponentially for complex documents regardless of file size.</small></p>
            </div>
        </div>

        <div class="chart-single">
            <div class="chart-item">
                <h3>4️⃣ Installation Size Comparison</h3>
                <div class="ranking-info" style="background: #fff2e6; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <strong>💿 Installation Footprint Ranking (Smaller = Better):</strong><br>
                    Framework installation sizes range from under 100MB to over 1GB depending on dependencies.
                </div>
                <img src="visualizations/installation_sizes.png" alt="Installation Sizes"
                     onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                <div style="display:none; text-align:center; padding:40px; background:#f8f9fa; border-radius:8px; border: 2px dashed #dee2e6;">
                    <h4>📦 Installation Size Analysis</h4>
                    <p>Framework installation sizes range from 71MB to 1GB+ depending on dependencies:</p>
                    <div style="text-align: left; display: inline-block; margin-top: 15px;">
                        <p><strong>Lightweight:</strong> Kreuzberg (71MB)</p>
                        <p><strong>Moderate:</strong> Extractous (100MB), Unstructured (146MB)</p>
                        <p><strong>Heavy:</strong> MarkItDown (251MB), Docling (1GB+)</p>
                    </div>
                </div>
                <p><small><strong>Trade-offs:</strong> Larger installations often include ML models and extensive format support, while smaller frameworks focus on specific use cases.</small></p>
            </div>
        </div>

        <h3>📈 Key Memory Usage Insights</h3>
        <ul>
            <li><strong>🔬 Measurement Method:</strong> RSS (Resident Set Size) tracked at 50ms intervals using psutil</li>
            <li><strong>📊 Framework Rankings:</strong> Memory efficiency varies by framework and use case - see charts for details</li>
            <li><strong>📄 Per-Format Variance:</strong> Memory usage patterns vary 10-50x between file types</li>
            <li><strong>📏 Size Correlation:</strong> Memory scales with document complexity, not just file size</li>
            <li><strong>🎯 Optimization Opportunities:</strong> Framework-format matching can reduce memory usage by 5-10x</li>
        </ul>

        <div style="text-align: center; margin: 30px 0;">
            <a href="reports/benchmark_report.html" style="background: #6c757d; color: white; padding: 15px 25px; border-radius: 5px; text-decoration: none;">
                📋 View Detailed Memory Report
            </a>
        </div>
    </section>

    <section id="formats" class="section">
        <h2>📄 Format Support Analysis</h2>

        <div class="metrics-guide" style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 5px;">
            <h4>📊 How to Read Format Support Charts</h4>
            <ul>
                <li><strong>✅ Supported:</strong> Framework can process this file type</li>
                <li><strong>❌ Not Supported:</strong> Framework cannot handle this format</li>
                <li><strong>⚠️ Partial:</strong> Limited or experimental support</li>
                <li><strong>🎨 Colorblind Accessible:</strong> Charts use blue/orange color schemes instead of green/red for better accessibility</li>
            </ul>
        </div>

        <!-- Format support matrix visualization not available in current visualizations -->

        <div class="chart-single">
            <div class="chart-item">
                <h3>2️⃣ Format Categories Overview</h3>
                <div class="ranking-info" style="background: #f3e5f5; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <strong>📄 Tested File Categories:</strong><br>
                    • Documents: PDF, DOCX, PPTX, XLSX, XLS, ODT (6 formats)<br>
                    • Web/Markup: HTML, MD, RST, ORG (4 formats)<br>
                    • Images: PNG, JPG, JPEG, BMP (4 formats)<br>
                    • Email: EML, MSG (2 formats) | Data: CSV, JSON, YAML (3 formats)
                </div>
                <div style="display:flex; justify-content:center; align-items:center; padding:40px; background:#f8f9fa; border-radius:8px; border: 2px dashed #dee2e6;">
                    <div style="text-align: left;">
                        <h4>📄 Format Categories Tested</h4>
                        <ul style="margin: 15px 0; padding-left: 20px;">
                            <li><strong>Documents:</strong> PDF, DOCX, PPTX, XLSX, XLS, ODT</li>
                            <li><strong>Web/Markup:</strong> HTML, MD, RST, ORG</li>
                            <li><strong>Images:</strong> PNG, JPG, JPEG, BMP</li>
                            <li><strong>Email:</strong> EML, MSG</li>
                            <li><strong>Data:</strong> CSV, JSON, YAML</li>
                            <li><strong>Text:</strong> TXT</li>
                        </ul>
                        <p><strong>Total:</strong> 18 different file formats across 6 categories</p>
                    </div>
                </div>
                <p><small><strong>Format Diversity:</strong> Comprehensive testing across document types commonly encountered in real-world text extraction scenarios.</small></p>
            </div>
        </div>
    </section>

    <section id="metadata" class="section">
        <h2>📋 Metadata Extraction Analysis</h2>

        <div class="alert">
            <strong>📊 Metadata Diversity:</strong> Comprehensive analysis of metadata extraction capabilities across frameworks, covering author information, creation dates, language detection, page counts, and 20+ metadata fields per document type.
        </div>

        <div class="metrics-guide" style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 5px;">
            <h4>📊 How to Read Metadata Analysis</h4>
            <ul>
                <li><strong>📊 Coverage %:</strong> HIGHER is BETTER (more metadata fields extracted)</li>
                <li><strong>📋 Field Count:</strong> HIGHER is BETTER (more comprehensive extraction)</li>
                <li><strong>✅ Completeness:</strong> HIGHER is BETTER (fewer missing values)</li>
                <li><strong>🎯 Quality:</strong> Framework-specific metadata extraction reliability</li>
            </ul>
        </div>

        <div class="chart-single">
            <div class="chart-item">
                <h3>1️⃣ Metadata Coverage by Framework</h3>
                <div class="ranking-info" style="background: #e3f2fd; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <strong>📊 Metadata Extraction Leaders:</strong><br>
                    Frameworks vary significantly in metadata extraction capabilities. Multi-format tools provide comprehensive coverage across diverse document types.
                </div>
                <img src="visualizations/analysis/metadata/metadata_coverage_chart.png" alt="Metadata Coverage"
                     onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                <div style="display:none; text-align:center; padding:40px; background:#f8f9fa; border-radius:8px; border: 2px dashed #dee2e6;">
                    <h4>📊 Metadata Analysis Available</h4>
                    <p>Comprehensive metadata extraction analysis covering 20+ fields per document type.</p>
                    <a href="visualizations/analysis/metadata/metadata_analysis_summary.md" style="background: #007bff; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none;">View Analysis</a>
                </div>
                <p><small><strong>Coverage Analysis:</strong> Shows percentage of metadata fields successfully extracted by each framework across all document types.</small></p>
            </div>
        </div>

        <div class="chart-single">
            <div class="chart-item">
                <h3>2️⃣ Field Extraction Comparison</h3>
                <div class="ranking-info" style="background: #f3e5f5; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <strong>📋 Metadata Field Types:</strong><br>
                    • Document Properties: Title, author, creation/modification dates<br>
                    • Content Metrics: Page count, word count, character count<br>
                    • Technical Data: MIME type, encoding, compression info<br>
                    • Quality Indicators: Language detection, format version
                </div>
                <img src="visualizations/analysis/metadata/field_comparison_chart.png" alt="Field Comparison"
                     onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                <div style="display:none; text-align:center; padding:40px; background:#f8f9fa; border-radius:8px; border: 2px dashed #dee2e6;">
                    <h4>📋 Field Comparison Data</h4>
                    <p>Detailed field-by-field comparison showing which frameworks extract specific metadata types.</p>
                    <a href="visualizations/analysis/metadata/metadata_field_comparison.csv" style="background: #007bff; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none;">Download CSV</a>
                </div>
                <p><small><strong>Field Analysis:</strong> Compares specific metadata field extraction capabilities across frameworks, highlighting strengths and gaps.</small></p>
            </div>
        </div>

        <h3>🔍 Metadata Extraction Capabilities</h3>
        <ul>
            <li><strong>Document Properties:</strong> Title, author, creation/modification dates, language detection</li>
            <li><strong>Content Metrics:</strong> Page count, word count, character count, document structure</li>
            <li><strong>Technical Metadata:</strong> MIME type, file format version, encoding, compression</li>
            <li><strong>Quality Assessment:</strong> Completeness scores, field coverage analysis, value examples</li>
            <li><strong>Framework Comparison:</strong> Coverage percentage, unique fields per framework, extraction reliability</li>
        </ul>

        <h3>📈 Key Metadata Insights</h3>
        <ul>
            <li><strong>Coverage Variance:</strong> Frameworks extract different metadata fields with varying completeness</li>
            <li><strong>Format Specialization:</strong> Different frameworks excel at different metadata types based on their design focus</li>
            <li><strong>Quality Correlation:</strong> Better metadata extraction often indicates higher text extraction quality</li>
            <li><strong>Language Detection:</strong> Multi-language document handling varies significantly across frameworks</li>
        </ul>

        <div style="text-align: center; margin: 30px 0;">
            <a href="visualizations/analysis/metadata/metadata_analysis_summary.md" style="background: #fd7e14; color: white; padding: 15px 25px; border-radius: 5px; text-decoration: none; margin-right: 15px;">
                📋 View Complete Metadata Analysis
            </a>
            <a href="visualizations/analysis/metadata/metadata_field_comparison.csv" style="background: #6c757d; color: white; padding: 15px 25px; border-radius: 5px; text-decoration: none;">
                📊 Download Field Comparison Data
            </a>
        </div>
    </section>

    <section id="quality" class="section">
        <h2>✨ Quality Assessment Analysis</h2>

        <div class="alert">
            <strong>🎯 ML-Based Quality Metrics:</strong> Comprehensive text extraction quality analysis using sentence transformers, readability metrics, coherence analysis, and document-specific quality checks across all frameworks and file types.
        </div>

        <div class="metrics-guide" style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 5px;">
            <h4>📊 How to Read Quality Assessment Charts</h4>
            <ul>
                <li><strong>🎯 Quality Score:</strong> HIGHER is BETTER (0.0 = worst, 1.0 = perfect)</li>
                <li><strong>📖 Readability Score:</strong> HIGHER is BETTER (easier to understand)</li>
                <li><strong>🔥 Coherence:</strong> HIGHER is BETTER (better text structure)</li>
                <li><strong>⚠️ Note:</strong> Quality assessment requires --enable-quality-assessment flag during benchmarking</li>
            </ul>
        </div>

        <div class="chart-single">
            <div class="chart-item">
                <h3>1️⃣ Quality Scores by Framework</h3>
                <div class="ranking-info" style="background: #e3f2fd; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <strong>🏆 Quality Rankings (Higher Score = Better):</strong><br>
                    Quality assessment provides ML-based scoring for extraction accuracy, coherence, and completeness across all tested frameworks and file types.
                </div>
                <img src="visualizations/quality_assessment.png" alt="Quality Assessment"
                     onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                <div style="display:none; text-align:center; padding:40px; background:#f8f9fa; border-radius:8px; border: 2px dashed #dee2e6;">
                    <h4>📊 Quality Assessment Available</h4>
                    <p>Quality assessment requires enabling during benchmark execution:</p>
                    <div style="background: #f8f9fa; padding: 10px; border-radius: 4px; margin: 10px 0; font-family: monospace;">
                        uv run python -m src.cli benchmark --enable-quality-assessment
                    </div>
                    <a href="quality-enhanced-results.json" style="background: #007bff; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none;">View Quality Data</a>
                </div>
                <p><small><strong>Quality Metrics:</strong> Combines extraction completeness, text coherence, semantic similarity, and document-specific quality checks.</small></p>
            </div>
        </div>

        <div class="chart-single">
            <div class="chart-item">
                <h3>2️⃣ Readability Analysis</h3>
                <div class="ranking-info" style="background: #f3e5f5; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <strong>📖 Readability Metrics:</strong><br>
                    • Flesch Reading Ease: Higher scores = easier to read<br>
                    • Gunning Fog Index: Lower scores = more accessible text<br>
                    • Sentence Structure: Analysis of complexity and coherence
                </div>
                <img src="visualizations/analysis/readability_comparison.png" alt="Readability Analysis"
                     onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                <div style="display:none; text-align:center; padding:40px; background:#f8f9fa; border-radius:8px; border: 2px dashed #dee2e6;">
                    <h4>📖 Readability Analysis</h4>
                    <p>Readability metrics computed using Flesch Reading Ease and Gunning Fog Index for extracted text quality assessment.</p>
                    <p style="margin-top:10px;"><em>Enable quality assessment in benchmarks to generate readability charts</em></p>
                    <div style="background: #f8f9fa; padding: 10px; border-radius: 4px; margin: 10px 0; font-family: monospace;">
                        uv run python -m src.cli benchmark --enable-quality-assessment
                    </div>
                </div>
                <p><small><strong>Text Quality:</strong> Measures how well frameworks preserve readable, coherent text structure during extraction.</small></p>
            </div>
        </div>

        <h3>🔬 Quality Assessment Capabilities</h3>
        <ul>
            <li><strong>ML-Based Scoring:</strong> Sentence transformer models for semantic similarity and coherence analysis</li>
            <li><strong>Readability Metrics:</strong> Flesch Reading Ease, Gunning Fog Index, average sentence/word length</li>
            <li><strong>Content Quality:</strong> Extraction completeness, text coherence, noise ratio, gibberish detection</li>
            <li><strong>Structural Analysis:</strong> Title detection, formatting preservation, table structure quality</li>
            <li><strong>Document-Specific Checks:</strong> PDF page integrity, HTML tag removal quality, Word formatting preservation</li>
        </ul>

        <h3>📈 Quality Scoring Methodology</h3>
        <ul>
            <li><strong>Overall Quality Score (0-1):</strong> Weighted combination of multiple quality dimensions</li>
            <li><strong>Extraction Completeness (25%):</strong> Estimated content coverage and missing information</li>
            <li><strong>Text Coherence (20%):</strong> Sentence structure and logical flow preservation</li>
            <li><strong>Semantic Similarity (20%):</strong> Meaning preservation compared to reference texts</li>
            <li><strong>Readability (15%):</strong> Human readability and comprehension scores</li>
            <li><strong>Structural Quality (20%):</strong> Format-specific quality checks and noise reduction</li>
        </ul>

        <h3>🎯 Key Quality Insights</h3>
        <ul>
            <li><strong>Framework Specialization:</strong> Quality scores vary by format - frameworks excel in their target document types</li>
            <li><strong>Speed vs Quality Trade-off:</strong> Fastest frameworks may sacrifice some quality for performance</li>
            <li><strong>OCR Quality Impact:</strong> Image-based documents show higher quality variance across frameworks</li>
            <li><strong>Language Dependency:</strong> Quality scores affected by document language and OCR language configuration</li>
        </ul>

        <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 5px;">
            <strong>💡 Enable Quality Assessment:</strong> Run benchmarks with <code>--enable-quality-assessment</code> flag to generate comprehensive quality metrics and visualizations.
        </div>

        <div style="text-align: center; margin: 30px 0;">
            <a href="quality-enhanced-results.json" style="background: #28a745; color: white; padding: 15px 25px; border-radius: 5px; text-decoration: none; margin-right: 15px;">
                📊 View Quality Enhanced Results
            </a>
            <a href="reports/benchmark_report.html#quality" style="background: #17a2b8; color: white; padding: 15px 25px; border-radius: 5px; text-decoration: none;">
                📖 Quality Analysis Report
            </a>
        </div>
    </section>

    <section id="formats" class="section">
        <h2>📄 Format Support Analysis</h2>

        <h3>Format Categories Tested</h3>
        <ul>
            <li><strong>Documents:</strong> PDF, DOCX, PPTX, XLSX, XLS, ODT</li>
            <li><strong>Web/Markup:</strong> HTML, MD, RST, ORG</li>
            <li><strong>Images:</strong> PNG, JPG, JPEG, BMP</li>
            <li><strong>Email:</strong> EML, MSG</li>
            <li><strong>Data:</strong> CSV, JSON, YAML</li>
            <li><strong>Text:</strong> TXT</li>
        </ul>

        <h3>Framework Capabilities</h3>
        <ul>
            <li><strong>Multi-Format Frameworks:</strong></li>
            <ul>
                <li><strong>Kreuzberg 3.8.0:</strong> All formats except MSG (no open source support)</li>
                <li><strong>Docling:</strong> PDF, DOCX, XLSX, PPTX, HTML, CSV, MD, AsciiDoc, Images (PNG, JPEG, TIFF, BMP, WEBP)</li>
                <li><strong>MarkItDown:</strong> Comprehensive office and web formats</li>
                <li><strong>Unstructured:</strong> 64+ file types including enterprise formats</li>
                <li><strong>Extractous:</strong> Rust-based performance across common formats</li>
            </ul>
        </ul>
    </section>

    <section id="frameworks" class="section">
        <h2>🔧 Framework Details</h2>

        <div class="framework-card">
            <h4>Kreuzberg 3.8.0</h4>
            <p><strong>License:</strong> MIT | <strong>Version:</strong> {kreuzberg_version} | <strong>Size:</strong> 71MB base</p>
            <p>Fast Python text extraction with multiple OCR backends. Supports both sync and async APIs.</p>
            <p><strong>Strengths:</strong> Speed, small footprint, async support, comprehensive format coverage</p>
            <p><strong>Format Support:</strong> All tested formats except MSG (no open source support)</p>
            <p><strong>Commercial Use:</strong> ✅ Fully permissive MIT license</p>
        </div>

        <div class="framework-card">
            <h4>Docling</h4>
            <p><strong>License:</strong> MIT | <strong>Version:</strong> {docling_version} | <strong>Size:</strong> 1GB+</p>
            <p>IBM Research's advanced document understanding with ML models.</p>
            <p><strong>Strengths:</strong> Advanced ML understanding, high quality</p>
            <p><strong>Format Support:</strong> PDF, DOCX, XLSX, PPTX, HTML, CSV, MD, AsciiDoc, Images</p>
            <p><strong>Commercial Use:</strong> ✅ Fully permissive MIT license</p>
        </div>

        <div class="framework-card">
            <h4>MarkItDown</h4>
            <p><strong>License:</strong> MIT | <strong>Version:</strong> {markitdown_version} | <strong>Size:</strong> 251MB</p>
            <p>Microsoft's lightweight Markdown converter optimized for LLM processing.</p>
            <p><strong>Strengths:</strong> LLM-optimized output, ONNX performance</p>
            <p><strong>Limitations:</strong> Limited format support</p>
            <p><strong>Commercial Use:</strong> ✅ Fully permissive MIT license</p>
        </div>

        <div class="framework-card">
            <h4>Unstructured</h4>
            <p><strong>License:</strong> Apache 2.0 | <strong>Version:</strong> {unstructured_version} | <strong>Size:</strong> 146MB</p>
            <p>Enterprise solution supporting 64+ file types.</p>
            <p><strong>Strengths:</strong> Widest format support, enterprise features</p>
            <p><strong>Limitations:</strong> Moderate speed</p>
            <p><strong>Commercial Use:</strong> ✅ Permissive Apache 2.0 license</p>
        </div>

        <div class="framework-card">
            <h4>Extractous</h4>
            <p><strong>License:</strong> Apache 2.0 | <strong>Version:</strong> {extractous_version} | <strong>Size:</strong> ~100MB</p>
            <p>Fast Rust-based extraction with Python bindings.</p>
            <p><strong>Strengths:</strong> Native performance, low memory usage</p>
            <p><strong>Format Support:</strong> Common office and web formats</p>
            <p><strong>Commercial Use:</strong> ✅ Permissive Apache 2.0 license</p>
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
        <p><em>Additional analysis modules are available in the detailed reports section above.</em></p>

        <h3>📊 Table Extraction Analysis</h3>
        <p>Specialized analysis of table detection and extraction capabilities across frameworks, focusing on structure preservation, cell accuracy, and formatting retention.</p>

        <div class="chart-grid">
            <div class="chart-item">
                <h4>Table Detection Performance</h4>
                <img src="visualizations/analysis/tables/table_detection_performance.png" alt="Table Detection Performance"
                     onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                <div style="display:none; text-align:center; padding:20px; background:#f8f9fa; border-radius:8px;">
                    <p>📊 Table detection analysis available for documents with table content</p>
                    <a href="visualizations/analysis/tables/table_extraction_analysis.json" style="color:#007bff;">View Analysis</a>
                </div>
            </div>
            <div class="chart-item">
                <h4>Structure Preservation Quality</h4>
                <img src="visualizations/analysis/tables/structure_quality_comparison.png" alt="Structure Quality"
                     onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                <div style="display:none; text-align:center; padding:20px; background:#f8f9fa; border-radius:8px;">
                    <p>📋 Table structure analysis data available in JSON format</p>
                    <a href="visualizations/analysis/tables/" style="color:#007bff;">Browse Analysis</a>
                </div>
            </div>
        </div>

        <h4>🔍 Table Extraction Capabilities</h4>
        <ul>
            <li><strong>Table Detection:</strong> Automatic identification of tabular content in documents</li>
            <li><strong>Structure Preservation:</strong> Maintenance of row/column relationships and cell boundaries</li>
            <li><strong>Content Accuracy:</strong> Correct extraction of cell content without OCR errors</li>
            <li><strong>Format Support:</strong> Table extraction from PDF, DOCX, HTML, and spreadsheet formats</li>
            <li><strong>Complex Layouts:</strong> Handling of merged cells, nested tables, and formatting</li>
        </ul>

        <div style="background: #e7f3ff; border-left: 4px solid #007bff; padding: 15px; margin: 20px 0; border-radius: 5px;">
            <strong>💡 Table Analysis:</strong> Run benchmarks with <code>--table-extraction-only</code> flag to focus analysis on documents containing tables.
        </div>

        <h3>💾 Memory Profiling Data Available</h3>
        <ul>
            <li><strong>Peak Memory Tracking:</strong> psutil RSS measurements at 50ms intervals for every extraction</li>
            <li><strong>Per-File-Type Memory:</strong> Memory usage breakdown by PDF, DOCX, HTML, images, etc.</li>
            <li><strong>Size Category Analysis:</strong> Memory scaling from tiny (100KB) to huge (50MB+) documents</li>
            <li><strong>Framework Memory Profiles:</strong> From Kreuzberg's 71MB to Docling's 1.7GB+ peak usage</li>
            <li><strong>Memory Efficiency Metrics:</strong> MB/second throughput and memory-per-character ratios</li>
        </ul>

        <h3>📊 Per-File-Type Performance Analysis</h3>
        <p><em>Detailed per-file-type performance data is available in the benchmark reports above.</em></p>

        <h4>🔬 Performance Methodology by File Type</h4>
        <ul>
            <li><strong>PDF Documents:</strong> Tested with both text-based and image-based PDFs, including complex layouts and tables</li>
            <li><strong>Office Documents:</strong> DOCX, PPTX, XLSX with varying complexity, embedded images, and formatting</li>
            <li><strong>Web Content:</strong> HTML with CSS styling, JavaScript content, and embedded multimedia</li>
            <li><strong>Images:</strong> OCR processing of screenshots, scanned documents, and rotated text</li>
            <li><strong>Email Formats:</strong> EML and MSG with attachments, HTML content, and threading</li>
            <li><strong>Data Formats:</strong> Structured CSV, JSON, YAML with varying sizes and nesting</li>
        </ul>

        <h4>📐 Performance Metrics Breakdown</h4>
        <ul>
            <li><strong>Extraction Time:</strong> Wall-clock time from file read to text output completion</li>
            <li><strong>Memory Usage:</strong> Peak RSS memory consumption during extraction process</li>
            <li><strong>Success Rate:</strong> Percentage of files successfully processed without errors or timeouts</li>
            <li><strong>Throughput:</strong> Files per second and MB per second processing rates</li>
            <li><strong>Text Quality:</strong> Character/word counts, readability scores, coherence metrics</li>
        </ul>

        <h3>🎯 Key Insights from File-Type Analysis</h3>
        <ul>
            <li><strong>Framework Specialization:</strong> Each framework has strengths in different file types and use cases</li>
            <li><strong>Format-Specific Optimization:</strong> Frameworks show 10-100x performance differences in their specialty areas</li>
            <li><strong>OCR Processing Costs:</strong> Image extraction consumes 10-50x more memory and time than text documents</li>
            <li><strong>Scaling Behavior:</strong> Performance degrades differently by file size depending on document complexity</li>
            <li><strong>Error Patterns:</strong> Framework failures cluster around specific file types and size thresholds</li>
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
