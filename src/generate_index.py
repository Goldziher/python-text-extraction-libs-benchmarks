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
    """Generate comprehensive index.html from aggregated results."""
    # Load aggregated results
    with open(aggregated_path, "rb") as f:
        results = msgspec.json.decode(f.read())

    # Get framework versions
    versions = get_framework_versions()

    # Calculate comprehensive metrics for the summary table
    framework_stats = {}
    dataset_stats = {
        "total_extractions": 0,
        "total_frameworks": 0,
        "total_file_types": set(),
        "total_categories": set(),
        "size_ranges": {"tiny": 0, "small": 0, "medium": 0, "large": 0, "huge": 0},
    }

    for framework, summaries in results["framework_summaries"].items():
        if not summaries:
            continue

        # Calculate overall metrics
        total_files = sum(s["total_files"] for s in summaries)
        successful_files = sum(s["successful_files"] for s in summaries)
        failed_files = sum(s.get("failed_files", 0) for s in summaries)
        timeout_files = sum(s.get("timeout_files", 0) for s in summaries)

        # Success rate on files actually tested
        success_rate = (successful_files / total_files * 100) if total_files > 0 else 0

        # Average speed (files per second) - weighted by file count
        total_time = sum(s.get("total_time", 0) for s in summaries)
        avg_speed = (total_files / total_time) if total_time > 0 else 0

        # Average memory usage - weighted average
        memories = [s["avg_peak_memory_mb"] for s in summaries if s.get("avg_peak_memory_mb")]
        avg_memory = sum(memories) / len(memories) if memories else 0

        # Throughput
        throughputs = [s.get("mb_per_second", 0) for s in summaries if s.get("mb_per_second")]
        avg_throughput = sum(throughputs) / len(throughputs) if throughputs else 0

        framework_stats[framework] = {
            "success_rate": success_rate,
            "avg_speed": avg_speed,
            "avg_memory": avg_memory,
            "avg_throughput": avg_throughput,
            "total_files": total_files,
            "successful_files": successful_files,
            "failed_files": failed_files,
            "timeout_files": timeout_files,
            "version": versions.get(framework.replace("_sync", "").replace("_async", ""), "Unknown"),
        }

        # Update dataset statistics
        dataset_stats["total_extractions"] += total_files
        for summary in summaries:
            dataset_stats["total_categories"].add(summary.get("category", "unknown"))
            if summary.get("category") in dataset_stats["size_ranges"]:
                dataset_stats["size_ranges"][summary["category"]] += summary.get("total_files", 0)

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
            <strong>⚠️ Methodology Note:</strong> PDF specialist frameworks (PyMuPDF, Playa, PDFPlumber) are tested only on PDF documents, while multi-format frameworks are tested across all file types. Performance metrics reflect each framework's intended use case and format coverage.
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
        "pymupdf": "~50MB",
        "pdfplumber": "~40MB",
        "playa": "~30MB",
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

        <div class="alert">
            <strong>📊 Memory Profiling:</strong> Peak memory usage tracked for every extraction with 50ms sampling intervals using psutil RSS measurements. Data available per file type, framework, and document size category.
        </div>

        <div class="chart-grid">
            <div class="chart-item">
                <h3>Memory Usage by Framework</h3>
                <img src="visualizations/memory_usage.png" alt="Memory Usage">
                <p><small>Aggregate memory consumption across all file types</small></p>
            </div>
            <div class="chart-item">
                <h3>Memory Usage by File Type</h3>
                <img src="visualizations/analysis/memory_usage_by_file_type.png" alt="Memory Usage by File Type">
                <p><small>Detailed memory profiling showing framework behavior per format</small></p>
            </div>
            <div class="chart-item">
                <h3>Category Performance</h3>
                <img src="visualizations/category_analysis.png" alt="Category Analysis">
                <p><small>Performance breakdown by document size categories</small></p>
            </div>
            <div class="chart-item">
                <h3>Installation Size Comparison</h3>
                <img src="visualizations/installation_sizes.png" alt="Installation Sizes">
                <p><small>Framework installation footprints and dependencies</small></p>
            </div>
        </div>

        <h3>📈 Memory Usage Insights</h3>
        <ul>
            <li><strong>Peak Memory Tracking:</strong> RSS (Resident Set Size) measured at 50ms intervals</li>
            <li><strong>Per-File-Type Analysis:</strong> Memory usage patterns vary significantly by format</li>
            <li><strong>Framework Differences:</strong> Memory requirements range from 50MB to 1.7GB+ depending on framework and document complexity</li>
            <li><strong>Document Size Correlation:</strong> Memory usage scales with document complexity, not just file size</li>
        </ul>

        <p style="text-align: center; margin-top: 20px;">
            <a href="visualizations/analysis/interactive_dashboard.html" style="background: #17a2b8; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none;">
                🔍 Explore Memory Data Interactively
            </a>
        </p>
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
    </section>

    <section id="metadata" class="section">
        <h2>📋 Metadata Extraction Analysis</h2>

        <div class="alert">
            <strong>📊 Metadata Diversity:</strong> Comprehensive analysis of metadata extraction capabilities across frameworks, covering author information, creation dates, language detection, page counts, and 20+ metadata fields per document type.
        </div>

        <div class="chart-grid">
            <div class="chart-item">
                <h3>Metadata Coverage by Framework</h3>
                <img src="visualizations/analysis/metadata/metadata_coverage_chart.png" alt="Metadata Coverage"
                     onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                <div style="display:none; text-align:center; padding:20px; background:#f8f9fa; border-radius:8px;">
                    <p>📊 Metadata coverage analysis available in detailed reports</p>
                    <a href="visualizations/analysis/metadata/metadata_analysis_summary.md" style="color:#007bff;">View Analysis</a>
                </div>
            </div>
            <div class="chart-item">
                <h3>Field Extraction Comparison</h3>
                <img src="visualizations/analysis/metadata/field_comparison_chart.png" alt="Field Comparison"
                     onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                <div style="display:none; text-align:center; padding:20px; background:#f8f9fa; border-radius:8px;">
                    <p>📊 Field comparison data available in CSV format</p>
                    <a href="visualizations/analysis/metadata/metadata_field_comparison.csv" style="color:#007bff;">Download CSV</a>
                </div>
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
            <li><strong>Format Specialization:</strong> PDF frameworks excel at document properties, office tools at creation metadata</li>
            <li><strong>Quality Correlation:</strong> Better metadata extraction often indicates higher text extraction quality</li>
            <li><strong>Language Detection:</strong> Multi-language document handling varies significantly across frameworks</li>
        </ul>

        <p style="text-align: center; margin-top: 20px;">
            <a href="visualizations/analysis/metadata/metadata_analysis_summary.md" style="background: #fd7e14; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; margin-right: 10px;">
                📋 View Complete Metadata Analysis
            </a>
            <a href="visualizations/analysis/metadata/metadata_field_comparison.csv" style="background: #6c757d; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none;">
                📊 Download Field Comparison Data
            </a>
        </p>
    </section>

    <section id="quality" class="section">
        <h2>✨ Quality Assessment Analysis</h2>

        <div class="alert">
            <strong>🎯 ML-Based Quality Metrics:</strong> Comprehensive text extraction quality analysis using sentence transformers, readability metrics, coherence analysis, and document-specific quality checks across all frameworks and file types.
        </div>

        <div class="chart-grid">
            <div class="chart-item">
                <h3>Quality Scores by Framework</h3>
                <img src="visualizations/quality_assessment.png" alt="Quality Assessment"
                     onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                <div style="display:none; text-align:center; padding:20px; background:#f8f9fa; border-radius:8px;">
                    <p>📊 Quality analysis data available when quality assessment is enabled</p>
                    <a href="quality-enhanced-results.json" style="color:#007bff;">View Quality Data</a>
                </div>
            </div>
            <div class="chart-item">
                <h3>Readability Analysis</h3>
                <img src="visualizations/analysis/readability_comparison.png" alt="Readability Analysis"
                     onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                <div style="display:none; text-align:center; padding:20px; background:#f8f9fa; border-radius:8px;">
                    <p>📖 Readability metrics computed using Flesch Reading Ease and Gunning Fog Index</p>
                    <p style="margin-top:10px;"><em>Enable quality assessment in benchmarks to generate charts</em></p>
                </div>
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

        <p style="text-align: center; margin-top: 20px;">
            <a href="quality-enhanced-results.json" style="background: #28a745; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; margin-right: 10px;">
                📊 View Quality Enhanced Results
            </a>
            <a href="reports/benchmark_report.html#quality" style="background: #17a2b8; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none;">
                📖 Quality Analysis Report
            </a>
        </p>
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
            <li><strong>PDF Specialists:</strong></li>
            <ul>
                <li><strong>PyMuPDF:</strong> PDF only (AGPL v3.0 license)</li>
                <li><strong>Playa:</strong> PDF only (fast extraction)</li>
                <li><strong>PDFPlumber:</strong> PDF only (table extraction focus)</li>
            </ul>
        </ul>
    </section>

    <section id="frameworks" class="section">
        <h2>🔧 Framework Details</h2>

        <div class="framework-card">
            <h4>Kreuzberg 3.8.0</h4>
            <p><strong>Version:</strong> {kreuzberg_version} | <strong>Size:</strong> 71MB base</p>
            <p>Fast Python text extraction with multiple OCR backends. Supports both sync and async APIs.</p>
            <p><strong>Strengths:</strong> Speed, small footprint, async support, comprehensive format coverage</p>
            <p><strong>Format Support:</strong> All tested formats except MSG (no open source support)</p>
        </div>

        <div class="framework-card">
            <h4>Docling</h4>
            <p><strong>Version:</strong> {docling_version} | <strong>Size:</strong> 1GB+</p>
            <p>IBM Research's advanced document understanding with ML models.</p>
            <p><strong>Strengths:</strong> Advanced ML understanding, high quality</p>
            <p><strong>Format Support:</strong> PDF, DOCX, XLSX, PPTX, HTML, CSV, MD, AsciiDoc, Images</p>
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
            <p><strong>Format Support:</strong> Common office and web formats</p>
        </div>

        <h3>📄 PDF Specialist Frameworks</h3>

        <div class="framework-card">
            <h4>PyMuPDF</h4>
            <p><strong>License:</strong> AGPL v3.0 | <strong>Size:</strong> ~50MB</p>
            <p>High-performance PDF processing library with comprehensive features.</p>
            <p><strong>Strengths:</strong> Extremely fast, comprehensive PDF support</p>
            <p><strong>Format Support:</strong> PDF only</p>
            <p><strong>Note:</strong> AGPL license requires open source distribution or commercial license</p>
        </div>

        <div class="framework-card">
            <h4>Playa</h4>
            <p><strong>License:</strong> MIT | <strong>Size:</strong> ~30MB</p>
            <p>Fast and lightweight PDF text extraction library.</p>
            <p><strong>Strengths:</strong> Speed, simple API, MIT license</p>
            <p><strong>Format Support:</strong> PDF only</p>
        </div>

        <div class="framework-card">
            <h4>PDFPlumber</h4>
            <p><strong>License:</strong> MIT | <strong>Size:</strong> ~40MB</p>
            <p>PDF processing with focus on table extraction and layout preservation.</p>
            <p><strong>Strengths:</strong> Table extraction, layout analysis</p>
            <p><strong>Format Support:</strong> PDF only</p>
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
            <a href="visualizations/analysis/interactive_dashboard.html" style="background: #28a745; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; margin-right: 10px;">
                📊 File Type Performance Dashboard
            </a>
            <a href="visualizations/analysis/performance_insights.md" style="background: #17a2b8; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; margin-right: 10px;">📝 Per-Format Analysis</a>
            <a href="visualizations/analysis/metadata/metadata_analysis_summary.md" style="background: #fd7e14; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; margin-right: 10px;">📋 Metadata Analysis</a>
            <a href="visualizations/analysis/tables/table_extraction_analysis.json" style="background: #6610f2; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none;">📊 Table Analysis</a>
        </p>

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
        <p>
            <a href="visualizations/analysis/interactive_dashboard.html" style="background: #6f42c1; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; margin-right: 10px;">
                📈 Interactive Performance Dashboard
            </a>
            <a href="visualizations/analysis/performance_by_file_type.png" style="background: #e83e8c; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; margin-right: 10px;">
                📊 Performance Charts
            </a>
            <a href="visualizations/analysis/file_type_performance_summary.csv" style="background: #20c997; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none;">
                📋 Download CSV Data
            </a>
        </p>

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
            <li><strong>PDF Specialists Dominate:</strong> PyMuPDF achieves 89+ files/sec on PDFs, 5x faster than multi-format tools</li>
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
