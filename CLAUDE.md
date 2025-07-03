# CLAUDE.md - Repository Knowledge Base

## Quick Reference

- **Main CLI**: `uv run python -m src.cli <command>`
- **Test Documents**: `test_documents/` (94 files, ~210MB)
- **CI Workflows**: `.github/workflows/benchmark-by-framework.yml` (recommended)
- **Key Timeouts**: 300s per extraction, 120min per CI job
- **Cache Clearing**: Kreuzberg cache cleared before each benchmark

## Repository Overview

This is the **Python Text Extraction Libraries Benchmarks 2025** repository, a comprehensive benchmarking suite designed to compare the performance of popular Python text extraction frameworks on macOS with CPU-only processing.

## Project Structure

```
python-text-extraction-libraries-benchmarks-2025/
├── src/                        # Main source code directory
│   ├── __init__.py            # Package initialization
│   ├── benchmark.py           # Core benchmarking engine
│   ├── check_installation_sizes.py  # Library size analysis tool
│   ├── cli.py                 # Command-line interface
│   ├── extractors.py          # Text extraction library wrappers
│   ├── profiler.py            # Performance profiling system
│   ├── reporting.py           # Results analysis and visualization
│   └── types.py               # Type definitions and data models
├── test_documents/            # Comprehensive test document collection
│   ├── pdfs/                  # 24 PDF files (17KB - 59MB)
│   ├── html/                  # 15 HTML files (multiple languages)
│   ├── office/                # 35 Office documents (DOCX, PPTX, XLSX, etc.)
│   ├── markdown/              # 9 Markdown/markup files
│   ├── images/                # 11 image files for OCR testing
│   ├── text/                  # 3 plain text files
│   └── csv_json_yaml/         # 4 data format files
├── results/                   # Benchmark results and visualizations
│   ├── charts/                # Generated performance charts
│   ├── detailed_results.csv   # Per-file extraction details
│   ├── summary_results.csv    # Aggregated statistics
│   ├── results.json           # Raw benchmark data (msgspec format)
│   └── summaries.json         # Summary statistics (msgspec format)
├── pyproject.toml             # Project configuration and dependencies
├── README.md                  # Project documentation
├── uv.lock                    # Dependency lock file
└── .pre-commit-config.yaml    # Pre-commit hook configuration
```

## Tested Frameworks

1. **Kreuzberg** (v3.3.0+)

    - Both synchronous and asynchronous APIs
    - Comprehensive format support with OCR capabilities
    - Smallest installation footprint (71MB)

1. **Docling** (v2.15.0+)

    - IBM Research Deep Search team
    - Advanced document understanding with ML models
    - Largest installation size (1GB+) due to PyTorch

1. **MarkItDown** (v0.0.1a2+)

    - Microsoft's lightweight Markdown converter
    - Optimized for LLM processing
    - Includes ONNX Runtime for ML inference (251MB)

1. **Unstructured** (v0.16.11+)

    - Unstructured.io's enterprise solution
    - Supports 64+ file types
    - Moderate installation size (146MB)

## Key Components

### 1. Benchmark Engine (`benchmark.py`)

- **BenchmarkRunner**: Orchestrates benchmark execution
- Supports both sync and async extractors
- Thread pool execution for sync extractors
- Comprehensive timeout and error handling
- Progress tracking with Rich console

### 2. Extractors (`extractors.py`)

- Wrapper classes for each library
- Consistent interface via Protocol pattern
- Graceful handling of missing dependencies
- Factory function for extractor instantiation

### 3. Performance Profiler (`profiler.py`)

- Context managers for sync/async profiling
- CPU usage sampling at 100ms intervals
- Memory (RSS) tracking with peak detection
- Uses psutil for cross-platform metrics

### 4. Reporting System (`reporting.py`)

- **BenchmarkReporter**: Generates comprehensive reports
- Console tables with Rich
- CSV exports for analysis
- Performance visualization charts:
    - Extraction time comparison
    - Memory usage comparison
    - Success rate comparison
    - Performance heatmap

### 5. CLI Interface (`cli.py`)

Commands:

- `benchmark`: Run comprehensive benchmarks
- `aggregate`: Combine results from multiple runs
- `report`: Generate markdown/HTML/JSON reports
- `visualize`: Create charts and dashboards
- `quality-assess`: Add ML-based quality metrics
- `list-frameworks`, `list-categories`, `list-file-types`: Show available options

## Test Document Collection

- **Total Files**: 94 documents
- **Total Size**: ~210MB
- **Formats**: PDF, HTML, DOCX, PPTX, XLSX, XLS, ODT, EPUB, MSG, EML, Markdown, Text, Images, CSV, JSON, YAML
- **Languages**: English, Hebrew, German, Chinese, Japanese, Korean
- **Special Features**:
    - OCR test images (including rotated text)
    - Mathematical equations and formulas
    - Complex tables and layouts
    - Copy-protected PDFs
    - Email attachments
    - Various text encodings

## Comprehensive Benchmark Methodology

### Document Categorization

Documents are automatically categorized by size:

- **Tiny**: < 100KB (15 files)
- **Small**: 100KB - 1MB (45 files)
- **Medium**: 1MB - 10MB (12 files)
- **Large**: 10MB - 50MB (20 files)
- **Huge**: > 50MB (2 files)

### Performance Metrics

- **Extraction Time**: Wall-clock time from start to completion
- **Memory Usage**: Peak and average RSS consumption
- **CPU Utilization**: Average percentage during processing
- **Success Rate**: Percentage of successful extractions
- **Throughput**: Files processed per second
- **Quality Score**: ML-based text quality assessment (0-1 scale)

### Framework Isolation

Each framework runs in a separate CI job:

- **No interference**: Slow frameworks don't block others
- **Clear visibility**: Per-framework success/failure status
- **Optimal timeouts**: 4-hour limit per framework job
- **Fair comparison**: Kreuzberg cache cleared between runs

### Profiling Approach

- **Multiple iterations**: 3 runs per document by default
- **Cold-start performance**: No warmup (realistic usage)
- **Resource monitoring**: 50ms sampling interval via psutil
- **Retry logic**: Exponential backoff on failures
- **Timeout protection**: 300s per extraction, 4h per job

## Usage Examples

### Running Comprehensive Benchmarks

```bash
# Run all frameworks on default categories (tiny, small, medium)
uv run python -m src.cli benchmark

# Test specific framework and category
uv run python -m src.cli benchmark \
  --framework kreuzberg_sync \
  --category small \
  --iterations 5

# Run with custom settings
uv run python -m src.cli benchmark \
  --framework docling,markitdown \
  --category tiny,small \
  --timeout 600 \
  --warmup-runs 2

# Test specific file types
uv run benchmark run --test-files-dir test_documents \
  --file-types pdf --file-types docx
```

### Generating Reports

```bash
# Generate report from existing results
uv run benchmark report --results-dir results --output-format table

# Export to CSV
uv run benchmark report --results-dir results --output-format csv

# Generate charts only
uv run benchmark report --results-dir results --output-format charts
```

### Checking Installation Sizes

```bash
# Analyze library installation footprints
python src/check_installation_sizes.py
```

## Development Setup

### Prerequisites

- Python 3.13+
- macOS or Linux
- 8GB+ RAM recommended

### Installation

```bash
# Clone repository
git clone <repository-url>
cd python-text-extraction-libraries-benchmarks-2025

# Install with uv (recommended)
uv sync --dev

# Install pre-commit hooks
uv run pre-commit install --hook-type commit-msg
uv run pre-commit install
```

### Development Tools

- **Ruff**: Fast Python linter and formatter
- **MyPy**: Static type checking
- **pytest**: Testing framework with async support
- **pre-commit**: Git hooks for code quality
- **msgspec**: Fast JSON serialization

## Technical Architecture

### Design Patterns

1. **Protocol-Based Design**: Type-safe duck-typing for extractors
1. **Async-First**: Core runner is async with thread pool for sync extractors
1. **Context Managers**: Clean resource management for profiling
1. **Factory Pattern**: Extractor instantiation
1. **Strategy Pattern**: Different extraction implementations

### Key Features

- Cross-platform compatibility
- Memory-efficient profiling
- Comprehensive error handling
- Type safety with Python 3.13+ features
- Extensible architecture for new frameworks
- Statistical analysis and visualization

## Configuration Files

### pyproject.toml

- Project metadata and dependencies
- Tool configurations (Ruff, MyPy, pytest)
- Script entry points

### .pre-commit-config.yaml

- Formatting with Ruff
- Type checking with MyPy
- Conventional commit messages
- Import sorting

## Results Structure

### JSON Files (msgspec format)

- **results.json**: Raw benchmark results
- **summaries.json**: Aggregated statistics

### CSV Files

- **detailed_results.csv**: Per-file extraction details
- **summary_results.csv**: Framework/file type summaries

### Charts Directory

- Extraction time comparisons
- Memory usage comparisons
- Success rate visualizations
- Performance heatmaps

## Known Patterns and Conventions

1. **File Extensions**: Used for file type detection
1. **Timeout Handling**: 300s default, configurable
1. **Memory Measurement**: RSS (Resident Set Size)
1. **CPU Sampling**: 100ms intervals
1. **Progress Display**: Rich console with live updates

## Future Extensibility

To add a new framework:

1. Create extractor class in `extractors.py`
1. Add to Framework enum in `types.py`
1. Register in `get_extractor()` factory
1. Add to dependencies in `pyproject.toml`

## Important Notes

- CPU-only benchmarking (no GPU acceleration)
- Single-threaded extraction (async where supported)
- Cold-start performance (no warmup runs)
- Real-world document collection for realistic results
- Platform: Primarily tested on macOS (Darwin)

## Repository Maintenance

- Keep test documents diverse and representative
- Update framework versions regularly
- Maintain backward compatibility in CLI
- Document any breaking changes
- Follow conventional commits for versioning

## Key Learnings & Optimizations

### Performance Observations

1. **Framework Speed Rankings** (on medium PDFs):

    - Kreuzberg: ~2 minutes for 24 extractions
    - Markitdown: Moderate speed
    - Unstructured: Slower but reliable
    - Docling: Very slow on complex PDFs (>60 min timeout)

1. **Cache Impact**:

    - Kreuzberg uses local cache (.kreuzberg directory)
    - Cache must be cleared for fair benchmarking
    - Significant performance difference with/without cache

1. **Timeout Requirements**:

    - Small documents: Usually complete in seconds
    - Medium documents: Can take 2-5 minutes per file for slow frameworks
    - CI jobs need 4-hour timeout for safety
    - Per-extraction timeout of 5 minutes is reasonable

### CI/CD Best Practices

1. **Framework Isolation**:

    - Run each framework in separate job
    - Prevents slow frameworks from blocking others
    - Better visibility and debugging

1. **Resource Management**:

    - Clear caches between runs
    - Monitor memory usage (some frameworks use 1GB+)
    - Use continue-on-error for robustness
    - 2-hour timeout per job (docling medium will likely timeout)

1. **Result Aggregation**:

    - Automatic collection from successful jobs only
    - Handles partial failures gracefully
    - Generates comprehensive reports regardless

### Common Issues & Solutions

1. **Docling Timeouts**:

    - Switch from markdown to text export for better performance
    - Consider reducing iterations for large documents
    - May need special handling for complex PDFs

1. **GitHub Actions Limits**:

    - Job timeout: 6 hours maximum
    - Workflow timeout: 72 hours maximum
    - Artifact retention: 90 days maximum

1. **Memory Issues**:

    - Some frameworks load entire document into memory
    - Monitor peak memory usage
    - Consider memory limits for large documents
