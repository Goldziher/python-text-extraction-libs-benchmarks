# Python Document Intelligence Framework CPU Benchmarks

<p align="center">
  <img src="docs/assets/logo.png" alt="Kreuzberg Logo" width="200">
</p>

<p align="center">
  <strong>Powered by Kreuzberg</strong> • Comprehensive document intelligence framework benchmarking
</p>

[![Benchmark Pipeline](https://github.com/Goldziher/python-text-extraction-libs-benchmarks/actions/workflows/benchmark-by-framework.yml/badge.svg)](https://github.com/Goldziher/python-text-extraction-libs-benchmarks/actions/workflows/benchmark-by-framework.yml)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Frameworks](https://img.shields.io/badge/frameworks-6-green.svg)](#tested-frameworks)
[![Documents](https://img.shields.io/badge/test_documents-94-blue.svg)](#benchmark-dataset)

> **🎯 [📊 VIEW LIVE BENCHMARK RESULTS →](https://benchmarks.kreuzberg.dev)**

## 🔍 What is This?

This repository provides **comprehensive, automated benchmarks** for Python document intelligence frameworks. We test popular multi-format document processing libraries against a diverse dataset of 94 real-world documents, measuring:

- **⚡ Performance**: Document processing speed, memory usage, CPU utilization
- **✅ Reliability**: Success rates, error handling, timeout behavior
- **📊 Quality**: Text extraction accuracy and completeness (optional)
- **🔧 Practicality**: Installation size, dependency count, format support

### 🤖 Automated CI/CD Benchmarking

Our GitHub Actions workflow automatically:

- **Runs benchmarks** every Monday at 6 AM UTC (or on-demand)
- **Tests each framework** in isolated environments to prevent interference
- **Generates comprehensive reports** with charts, tables, and analysis
- **Deploys results** to GitHub Pages for easy viewing
- **Stores all raw data** in the repository for transparency and reproducibility

### 📂 All Data is Open

- **Raw benchmark results**: Available in `results/` directory as JSON/CSV
- **Test documents**: 94 files in `test_documents/` (~210MB total)
- **Visualizations**: Charts and graphs in `results/charts/`
- **Historical data**: Track performance trends over time via git history
- **Reproducible**: Run the same benchmarks locally with our CLI

## 🚀 Quick Start

### Install and Run Benchmarks Locally

```bash
# Clone the repository
git clone https://github.com/Goldziher/python-text-extraction-libs-benchmarks.git
cd python-text-extraction-libs-benchmarks

# Install base dependencies only
uv sync

# Install specific frameworks (recommended due to conflicts)
uv sync --extra kreuzberg           # Kreuzberg framework
uv sync --extra kreuzberg-ocr       # Kreuzberg with OCR backends
uv sync --extra extractous          # Extractous framework
uv sync --extra unstructured        # Unstructured framework
uv sync --extra markitdown          # MarkItDown framework
uv sync --extra docling             # Docling framework (may conflict with kreuzberg)

# Install all compatible frameworks (excludes docling due to conflicts)
uv sync --extra all

# Run benchmarks for installed frameworks
uv run python -m src.cli benchmark

# Test specific frameworks
uv run python -m src.cli benchmark --framework kreuzberg_sync,extractous --category small

# Generate reports from results
uv run python -m src.cli report --output-format html
uv run python -m src.cli visualize
```

#### Framework Compatibility Notes

Due to dependency conflicts between frameworks:
- **kreuzberg** (3.10.1+) and **docling** cannot be installed together (lxml version conflict)
- Install frameworks individually or use `--extra all` for all compatible frameworks
- The benchmarking tool will gracefully skip frameworks that aren't installed

### 📋 CLI Commands

Our comprehensive CLI provides full control over benchmarking:

```bash
# List available commands
uv run python -m src.cli --help

# Benchmarking commands
uv run python -m src.cli benchmark          # Run benchmarks
uv run python -m src.cli list-frameworks    # Show available frameworks
uv run python -m src.cli list-categories    # Show document categories
uv run python -m src.cli list-file-types    # Show supported file types

# Analysis and reporting
uv run python -m src.cli report             # Generate reports
uv run python -m src.cli visualize          # Create charts
uv run python -m src.cli aggregate          # Combine results
uv run python -m src.cli quality-assess     # Add quality metrics

# Advanced options
uv run python -m src.cli benchmark \
  --framework kreuzberg_sync,extractous \
  --category tiny,small,medium \
  --iterations 5 \
  --timeout 600 \
  --enable-profiling \
  --enable-quality-assessment
```

## 📊 Benchmark Results Overview

> **[📈 View Full Interactive Results →](https://benchmarks.kreuzberg.dev)**

### What's in the Results?

- **⚡ Performance Rankings**: Speed comparison across all frameworks and file types
- **💾 Resource Usage**: Memory consumption and CPU utilization analysis
- **✅ Success Rates**: Reliability metrics and failure analysis
- **📊 Interactive Dashboards**: Explore data by framework, file type, and size
- **🔍 Detailed Breakdowns**: Per-file extraction times and error logs
- **📈 Trend Analysis**: Performance over multiple iterations
- **📋 Raw Data**: All benchmark data available for download and analysis

## 🔬 Tested Frameworks

We benchmark the following multi-format document intelligence frameworks:

1. **Kreuzberg** (v3.8.0+)

    - Both synchronous and asynchronous APIs
    - Multiple OCR backends (Tesseract, EasyOCR, PaddleOCR)
    - Lightweight installation (71MB)

1. **Extractous** (v0.1.0+)

    - Rust-based with Python bindings
    - Native performance characteristics
    - Supports 1000+ formats via Apache Tika

1. **Unstructured** (v0.18.5+)

    - Enterprise-focused solution
    - Supports 64+ file types including emails
    - Moderate installation size (146MB)

1. **MarkItDown** (v0.0.1a2+)

    - Microsoft's Markdown converter
    - Includes ONNX Runtime for ML inference
    - Optimized for LLM preprocessing

1. **Docling** (v2.41.0+)

    - IBM Research's document understanding
    - Advanced ML models included
    - Largest installation (1GB+)

Each framework is tested with identical documents and conditions for fair comparison.

## 📊 Benchmark Dataset

Our test suite includes 94 real-world documents (~210MB total) across diverse formats:

### Document Categories

- **📄 Office**: DOCX, PPTX, XLSX, XLS, ODT (35 files)
- **📑 PDF**: Academic papers, reports, scanned documents (24 files)
- **🌐 Web**: HTML pages with various complexities (15 files)
- **🖼️ Images**: PNG, JPG, JPEG, BMP for OCR testing (11 files)
- **📧 Email**: EML and MSG with attachments (6 files)
- **📝 Text/Markup**: MD, RST, ORG, TXT (12 files)
- **📊 Data**: CSV, JSON, YAML (4 files)

### Size Distribution

- **Tiny**: < 100KB (15 files) - Quick extraction tests
- **Small**: 100KB - 1MB (45 files) - Typical documents
- **Medium**: 1MB - 10MB (12 files) - Complex documents
- **Large**: 10MB - 50MB (20 files) - Stress tests
- **Huge**: > 50MB (2 files) - Performance limits

### Multi-Language Support

Documents in English, Hebrew, German, Chinese, Japanese, and Korean to test language-specific extraction capabilities.

## 🔧 Advanced Usage

### Benchmark Specific File Types

```bash
# Test only PDF files
uv run python -m src.cli benchmark --file-types pdf

# Test multiple file types
uv run python -m src.cli benchmark --file-types pdf --file-types docx --file-types html

# Test by format tier (universal formats supported by all frameworks)
uv run python -m src.cli benchmark --format-tier universal
```

### Framework-Specific Options

```bash
# Test Kreuzberg with different OCR backends
uv run python -m src.cli benchmark \
  --framework kreuzberg_tesseract,kreuzberg_easyocr,kreuzberg_paddleocr \
  --category images

# Test async vs sync implementations
uv run python -m src.cli benchmark \
  --framework kreuzberg_sync,kreuzberg_async \
  --enable-profiling
```

### Analysis and Quality Assessment

```bash
# Run with quality assessment (slower but provides accuracy metrics)
uv run python -m src.cli benchmark --enable-quality-assessment

# Generate quality-enhanced reports
uv run python -m src.cli quality-assess --results-file results/results.json

# Create custom visualizations
uv run python -m src.cli visualize \
  --results-file results/aggregated_results.json \
  --output-dir custom_charts/
```

## 🔬 Benchmarking Methodology

### How We Test

1. **Isolated Environments**: Each framework runs in a separate CI job to prevent interference
1. **Cold Start**: No warmup runs - we measure real-world first-use performance
1. **Resource Monitoring**: Track memory (RSS) and CPU usage at 50ms intervals
1. **Timeout Protection**: 300s per file, 2 hours per framework job
1. **Multiple Iterations**: Default 3 runs per file to ensure consistency
1. **Error Tracking**: Capture and categorize all failures and timeouts

### Performance Metrics

- **Extraction Time**: Wall-clock time from start to completion
- **Memory Usage**: Peak RSS (Resident Set Size) during extraction
- **CPU Utilization**: Average CPU percentage during processing
- **Throughput**: Files/second and MB/second processing rates
- **Success Rate**: Percentage of files extracted without errors

### Quality Assessment (Optional)

When enabled with `--enable-quality-assessment`:

- **Readability Scores**: Flesch Reading Ease, Gunning Fog Index
- **Text Coherence**: Sentence structure and flow analysis
- **Completeness**: Estimated content coverage
- **Noise Detection**: Garbage text and encoding issues

## 📈 CI/CD and Data Availability

### Automated Benchmarking

Our GitHub Actions workflow (`benchmark-by-framework.yml`):

- **Runs automatically** every Monday at 6 AM UTC
- **Can be triggered manually** via GitHub Actions UI
- **Tests each framework** in parallel with 2-hour timeouts
- **Generates reports** and deploys to GitHub Pages
- **Stores all data** in the repository for analysis

### Available Data

All benchmark data is freely available:

```bash
# Raw results (JSON format)
results/results.json
results/summaries.json
results/aggregated_results.json

# CSV exports for analysis
results/detailed_results.csv
results/summary_results.csv

# Visualizations
results/charts/*.png
results/charts/interactive_dashboard.html

# Framework metadata
visualizations/analysis/metadata/
visualizations/analysis/tables/
```

### Reproducing Results

```bash
# Run the exact same benchmarks locally
uv run python -m src.cli benchmark --framework all

# Or download our results
wget https://github.com/Goldziher/python-text-extraction-libs-benchmarks/raw/main/results/aggregated_results.json
```

## 📋 Format Support Analysis

### Framework-Specific Capabilities

Each framework supports different file formats. Our benchmarks test:

| Framework    | Tested Formats | Notable Limitations   |
| ------------ | -------------- | --------------------- |
| Kreuzberg    | 17/18 formats  | No MSG support        |
| Extractous   | Most formats   | Some edge cases       |
| Unstructured | 64+ formats    | Full support          |
| MarkItDown   | Office & web   | Limited formats       |
| Docling      | 10 formats     | No email/data formats |

### Format Tiers

For fair comparison across frameworks:

```bash
# Tier 1: Universal formats (supported by all frameworks)
uv run python -m src.cli benchmark --format-tier universal

# Tier 2: Common formats (supported by most frameworks)
uv run python -m src.cli benchmark --format-tier common

# All formats (shows full capabilities)
uv run python -m src.cli benchmark --format-tier all
```

## 🤝 Contributing

We welcome contributions! Areas of interest:

- **New frameworks**: Add support for emerging document intelligence libraries
- **More test documents**: Expand our dataset with edge cases
- **Performance optimizations**: Improve benchmarking efficiency
- **Analysis tools**: Enhanced visualization and reporting capabilities
- **Multi-language tests**: Expand language coverage

```bash
# Set up development environment
uv sync --all-extras
uv run pre-commit install

# Run tests
uv run pytest

# Submit PR with your improvements!
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Powered by [Kreuzberg](https://github.com/Goldziher/kreuzberg) - Fast Python document intelligence
- Test documents from various public sources
- Framework maintainers for their excellent libraries
- GitHub Actions for CI/CD infrastructure
