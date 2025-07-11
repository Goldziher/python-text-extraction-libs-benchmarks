# CLI Command Guide

This guide provides comprehensive examples for using the Python Text Extraction Libraries Benchmarking CLI.

## Table of Contents

- [Installation](#installation)
- [Core Commands](#core-commands)
- [Analysis Commands](#analysis-commands)
- [Utility Commands](#utility-commands)
- [Advanced Usage](#advanced-usage)

## Installation

```bash
# Clone and install
git clone <repository-url>
cd python-text-extraction-libraries-benchmarks-2025
uv sync --dev
```

## Core Commands

### `benchmark` - Run Extraction Benchmarks

Run comprehensive benchmarks across frameworks and document categories.

```bash
# Basic usage - benchmark all frameworks on default categories
uv run python -m src.cli benchmark

# Specific frameworks
uv run python -m src.cli benchmark --framework kreuzberg_sync,extractous,unstructured

# Specific categories
uv run python -m src.cli benchmark --category tiny,small,medium

# Custom settings
uv run python -m src.cli benchmark \
  --framework docling,markitdown \
  --category small \
  --iterations 5 \
  --timeout 120 \
  --output-dir custom_results

# Format tier testing (only test commonly supported formats)
uv run python -m src.cli benchmark --format-tier universal  # Formats supported by all
uv run python -m src.cli benchmark --format-tier common     # Formats supported by most
uv run python -m src.cli benchmark --format-tier all        # Test everything

# Enable quality assessment (saves extracted text)
uv run python -m src.cli benchmark --enable-quality-assessment
```

### `aggregate` - Combine Multiple Benchmark Runs

Aggregate results from multiple benchmark runs for statistical analysis.

```bash
# Basic aggregation
uv run python -m src.cli aggregate results_dir/

# Specify output directory
uv run python -m src.cli aggregate results_dir/ --output-dir aggregated_results/

# Aggregate from multiple sources
uv run python -m src.cli aggregate run1/ run2/ run3/ --output-dir combined/
```

### `report` - Generate Reports from Results

Create detailed reports in various formats.

```bash
# Generate markdown report
uv run python -m src.cli report --results-dir results/ --output-format markdown

# Generate HTML report with charts
uv run python -m src.cli report --results-dir results/ --output-format html

# Generate JSON report for programmatic access
uv run python -m src.cli report --results-dir results/ --output-format json

# Generate all formats
uv run python -m src.cli report --results-dir results/ --output-format all
```

### `visualize` - Create Performance Charts

Generate visualization charts from benchmark results.

```bash
# Basic visualization
uv run python -m src.cli visualize --aggregated-file results/aggregated.json

# Custom output directory
uv run python -m src.cli visualize \
  --aggregated-file results/aggregated.json \
  --output-dir custom_charts/

# Specific chart types
uv run python -m src.cli visualize \
  --aggregated-file results/aggregated.json \
  --chart-types extraction_time,memory_usage,success_rate
```

## Analysis Commands

### `metadata-analysis` - Analyze Metadata Extraction

Analyze metadata extraction capabilities across frameworks.

```bash
# Basic metadata analysis
uv run python -m src.cli metadata-analysis

# Custom directories
uv run python -m src.cli metadata-analysis \
  --results-dir benchmark_results/ \
  --output-dir metadata_reports/

# Exclude specific frameworks (e.g., during updates)
uv run python -m src.cli metadata-analysis --exclude-kreuzberg
```

**Output files:**

- `metadata_coverage.json` - Detailed coverage statistics by framework
- `metadata_field_comparison.csv` - Field-by-field comparison matrix
- `metadata_quality.json` - Quality metrics and field examples
- `metadata_analysis_summary.md` - Human-readable summary report

### `file-type-analysis` - Analyze Performance by File Type

Analyze framework performance broken down by file type.

```bash
# Basic file type analysis
uv run python -m src.cli file-type-analysis

# Generate interactive dashboard
uv run python -m src.cli file-type-analysis --interactive

# Custom output format
uv run python -m src.cli file-type-analysis --output-format csv

# Multiple output formats
uv run python -m src.cli file-type-analysis --output-format json --output-format charts
```

**Output options:**

- `table` - Console table display
- `csv` - Detailed CSV exports
- `json` - JSON data for programmatic access
- `charts` - Performance visualization charts
- `--interactive` - Interactive HTML dashboard

### `quality-assess` - Add Quality Metrics

Enhance benchmark results with quality assessment metrics.

```bash
# Add quality metrics to existing results
uv run python -m src.cli quality-assess \
  --results-file results/results.json \
  --output-file results/enhanced_results.json

# Compare against reference extractions
uv run python -m src.cli quality-assess \
  --results-file results/results.json \
  --reference-dir reference_texts/ \
  --output-file results/quality_enhanced.json

# Custom ML model for quality scoring
uv run python -m src.cli quality-assess \
  --results-file results/results.json \
  --model-name microsoft/deberta-v3-base \
  --output-file results/ml_quality.json
```

## Utility Commands

### `list-frameworks` - Show Available Frameworks

```bash
# List all available frameworks
uv run python -m src.cli list-frameworks

# Example output:
# Available frameworks:
#   - kreuzberg_sync: Synchronous Kreuzberg extractor
#   - kreuzberg_async: Asynchronous Kreuzberg extractor
#   - docling: IBM Docling with ML models
#   - markitdown: Microsoft MarkItDown
#   - unstructured: Unstructured.io
#   - extractous: Rust-based Extractous
```

### `list-categories` - Show Document Categories

```bash
# List all document categories
uv run python -m src.cli list-categories

# Example output:
# Available categories:
#   - tiny: Documents < 100KB (15 files)
#   - small: Documents 100KB-1MB (45 files)
#   - medium: Documents 1MB-10MB (12 files)
#   - large: Documents 10MB-50MB (20 files)
#   - huge: Documents > 50MB (2 files)
```

### `list-file-types` - Show Supported File Types

```bash
# List all file types in test documents
uv run python -m src.cli list-file-types

# Example output:
# Available file types:
#   - pdf: PDF documents (24 files)
#   - docx: Word documents (12 files)
#   - html: HTML files (15 files)
#   - txt: Plain text (3 files)
#   ...
```

## Advanced Usage

### Chaining Commands

```bash
# Run benchmark, then analyze results
uv run python -m src.cli benchmark --framework all --category small && \
uv run python -m src.cli metadata-analysis && \
uv run python -m src.cli file-type-analysis --interactive

# Full pipeline with quality assessment
uv run python -m src.cli benchmark --enable-quality-assessment && \
uv run python -m src.cli quality-assess \
  --results-file results/results.json \
  --output-file results/enhanced.json && \
uv run python -m src.cli report --results-dir results/ --output-format all
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Run benchmarks
  run: |
    uv sync
    uv run python -m src.cli benchmark \
      --framework ${{ matrix.framework }} \
      --category tiny,small \
      --iterations 3 \
      --timeout 300

- name: Analyze results
  run: |
    uv run python -m src.cli metadata-analysis
    uv run python -m src.cli file-type-analysis --output-format json
    uv run python -m src.cli report --output-format markdown
```

### Custom Scripts

```python
# Use CLI components in custom scripts
from src.cli import benchmark, metadata_analysis
from pathlib import Path

# Run benchmark programmatically
results = benchmark(
    framework=['extractous', 'unstructured'],
    category=['small'],
    iterations=5
)

# Analyze metadata
metadata_analysis(
    results_dir=Path('results'),
    output_dir=Path('analysis')
)
```

## Tips and Best Practices

1. **Start Small**: Test with `--category tiny` first to verify setup
1. **Use Format Tiers**: Use `--format-tier universal` for fair comparisons
1. **Multiple Iterations**: Use at least 3 iterations for reliable results
1. **Save Extracted Text**: Use `--enable-quality-assessment` for detailed analysis
1. **Monitor Resources**: Some frameworks use significant memory (1GB+)
1. **Clear Cache**: Kreuzberg cache is automatically cleared between runs

## Troubleshooting

```bash
# Verbose output for debugging
uv run python -m src.cli benchmark --framework extractous --category tiny -v

# Continue on errors
uv run python -m src.cli benchmark --continue-on-error

# Increase timeout for slow frameworks
uv run python -m src.cli benchmark --timeout 600

# Check framework installation
uv run python -m src.cli list-frameworks
```

## Environment Variables

```bash
# Set default output directory
export BENCHMARK_OUTPUT_DIR=/path/to/results

# Set default timeout
export BENCHMARK_TIMEOUT=300

# Enable debug logging
export BENCHMARK_DEBUG=1
```

For more details, see the main README.md and CLAUDE.md documentation.
