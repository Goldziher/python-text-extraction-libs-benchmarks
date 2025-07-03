# CLAUDE.md - Repository Knowledge Base

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

- Commands: `run`, `report`, `list-frameworks`, `list-file-types`
- Flexible framework and file type selection
- Configurable timeouts and output directories
- Built with Click framework

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

## Benchmark Methodology

### Performance Metrics

- **Extraction Time**: Wall-clock time from start to completion
- **Memory Usage**: Peak RSS memory consumption
- **CPU Utilization**: Average percentage during processing
- **Success Rate**: Percentage of successful extractions
- **Text Quality**: Character count of extracted text

### Profiling Approach

- Single-run measurements (no warmup)
- Garbage collection before each test
- 100ms sampling interval for resource monitoring
- Timeout protection (default: 300s)

## Usage Examples

### Running Benchmarks

```bash
# Test all frameworks on all file types
uv run benchmark run --test-files-dir test_documents

# Test specific frameworks
uv run benchmark run --test-files-dir test_documents \
  --frameworks kreuzberg_sync --frameworks markitdown

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
