# Python Text Extraction Libraries Benchmarks 2025

A comprehensive benchmarking suite comparing the performance of popular Python text extraction frameworks on macOS with CPU-only processing.

## Overview

This project provides systematic performance comparisons between leading Python text extraction libraries, focusing on real-world usage patterns and resource efficiency. The benchmarks are designed to help developers choose the most appropriate framework for their specific use cases.

## Tested Frameworks

### 🏆 [Kreuzberg](https://github.com/Goldziher/kreuzberg) v3.3.0+

- **Sync & Async**: Both synchronous and asynchronous APIs tested
- **Features**: PDF, images, office documents, OCR support with multiple backends
- **Strength**: Comprehensive format support with async capabilities

### 🔵 [Docling](https://github.com/docling-project/docling) v2.15.0+

- **Developer**: IBM Research Deep Search team
- **Features**: Advanced document understanding, table extraction, markdown export
- **Strength**: Enterprise-grade document processing with structured output

### 🟢 [MarkItDown](https://github.com/microsoft/markitdown) v0.0.1a2+

- **Developer**: Microsoft
- **Features**: Lightweight converter to Markdown for LLM processing
- **Strength**: Fast, simple conversion optimized for AI workflows

### 🟡 [Unstructured](https://github.com/Unstructured-IO/unstructured) v0.16.11+

- **Developer**: Unstructured.io
- **Features**: 35+ sources, 64+ file types, enterprise ETL capabilities
- **Strength**: Broad format support with enterprise features

## Methodology

### Test Documents Collection

Our benchmarks use a comprehensive collection of 94 test documents across multiple formats, languages, and complexity levels. This diverse dataset ensures realistic performance measurements that reflect real-world usage scenarios.

#### Document Categories

##### PDF Documents (24 files)

- **Size range**: 17KB to 59MB
- **Types**: Academic papers, technical manuals, presentations, scanned documents
- **Special cases**: OCR test PDFs (rotated at 90°, 180°, 270°), copy-protected PDFs, PDFs with embedded images and tables
- **Examples**: Intel Architecture Manual (50MB), Proof of Concept magazine (59MB), simple memos (13KB)

##### HTML Documents (15 files)

- **Languages**: English, Hebrew, German, Chinese
- **Sources**: Wikipedia Good Articles of varying lengths
- **Size range**: 70KB to 1.6MB
- **Examples**: World War II article (1.1MB), consciousness philosophy article (715KB), shortest Good Article (70KB)

##### Office Documents (35 files)

- **DOCX** (14 files): Tables, equations, headers, formatting, text boxes, EMF graphics
- **PPTX** (4 files): Standard presentations, image-heavy slides, malformed documents
- **XLSX** (2 files): Spreadsheets with formulas and data
- **XLS** (1 file): Legacy Excel format
- **ODT** (2 files): OpenDocument text format
- **EPUB** (2 files): E-book format including a 31.6MB book
- **MSG** (3 files): Outlook message format with attachments
- **EML** (1 file): Standard email format

##### Markdown & Text Documents (9 files)

- **Markdown**: README files, tables, converted Wikipedia articles
- **Plain text**: Simple text, War and Peace excerpt, various encodings
- **Markup formats**: reStructuredText, Org-mode

##### Images (11 files)

- **Formats**: JPEG, PNG, BMP
- **Content**: OCR test images, multi-language text (Chinese, Japanese, Korean), document scans
- **Special cases**: Vertical Japanese text, mixed English-Korean text

##### Data Formats (4 files)

- **CSV**: Simple data tables
- **JSON**: Structured data
- **YAML**: Configuration format
- **XLSX**: Excel with CSV data

#### Language Coverage

- **Primary**: English
- **International**: Hebrew (ישראל, תל אביב), German (Deutschland, Berlin), Chinese (中国, 北京市)
- **OCR Languages**: Japanese, Korean, Chinese

#### Document Characteristics

- **Size range**: 91 bytes to 59MB
- **Total collection size**: ~210MB
- **Special features**:
    - Mathematical equations and formulas
    - Complex tables and layouts
    - Rotated and skewed text
    - Copy protection
    - Multiple languages and scripts
    - Embedded images and graphics
    - Email attachments
    - Various text encodings

### Test Environment

- **Platform**: macOS (Darwin 24.5.0)
- **Processing**: CPU-only (no GPU acceleration)
- **Python**: 3.13+
- **Concurrency**: Single-threaded per extraction (async where supported)

### Benchmarking Approach

#### 1. **Performance Metrics**

- **Extraction Time**: Wall-clock time from start to completion
- **Memory Usage**: Peak RSS memory consumption during extraction
- **CPU Utilization**: Average CPU percentage during processing
- **Success Rate**: Percentage of successful extractions

#### 2. **Profiling Method**

```python
# Synchronous profiling
with profile_performance() as metrics:
    extracted_text = extractor.extract_text(file_path)

# Asynchronous profiling
async with AsyncPerformanceProfiler() as metrics:
    extracted_text = await extractor.extract_text(file_path)
```

#### 3. **Resource Monitoring**

- **Memory**: Peak RSS usage via `psutil.Process().memory_info()`
- **CPU**: Average percentage via `psutil.Process().cpu_percent()`
- **Sampling**: 100ms intervals during extraction
- **Baseline**: Garbage collection forced before each test

#### 4. **Error Handling**

- **Timeouts**: Configurable per-extraction timeout (default: 300s)
- **Graceful Degradation**: Missing dependencies handled transparently
- **Retry Logic**: No retries (single-shot measurements)

### Test Document Selection Criteria

1. **Size Diversity**: Documents from 91 bytes to 59MB to test memory efficiency
1. **Format Coverage**: All major document formats used in enterprise and academic settings
1. **Language Variety**: Multiple languages and scripts to test Unicode handling
1. **Complexity Levels**: From simple text to complex layouts with tables, images, and formulas
1. **Real-World Examples**: Actual documents from Wikipedia, technical manuals, and open-source projects
1. **Edge Cases**: Rotated text, copy protection, malformed documents, special encodings

### Statistical Approach

- **Single Run**: Each framework tested once per file
- **Reproducibility**: Fixed test documents for consistent comparison
- **No Warmup**: Cold-start performance measured (realistic usage)

## Installation & Setup

### Prerequisites

- Python 3.13+
- macOS (tested) or Linux
- 8GB+ RAM recommended for comprehensive tests

### Quick Start

```bash
# Clone repository
git clone <repository-url>
cd python-text-extraction-libraries-benchmarks-2025

# Install with uv (recommended)
uv sync --dev

# Or with pip
pip install -e ".[dev]"

# Install pre-commit hooks
uv run pre-commit install --hook-type commit-msg
uv run pre-commit install
```

### Optional Dependencies

Some frameworks require additional system dependencies:

```bash
# For OCR support (Kreuzberg)
brew install tesseract

# For advanced table extraction (Kreuzberg + GMFT)
# GPU support recommended but not required

# For advanced document processing features
```

## Usage Guide

### Running Benchmarks

#### 1. **List Available Options**

```bash
# Show supported frameworks
uv run benchmark list-frameworks

# Show supported file types
uv run benchmark list-file-types
```

#### 2. **Basic Benchmark Run**

```bash
# Test all frameworks on all file types
uv run benchmark run --test-files-dir sample_documents

# Test specific frameworks
uv run benchmark run \
  --test-files-dir sample_documents \
  --frameworks kreuzberg_sync \
  --frameworks kreuzberg_async \
  --frameworks markitdown

# Test specific file types
uv run benchmark run \
  --test-files-dir sample_documents \
  --file-types pdf \
  --file-types docx \
  --file-types html
```

#### 3. **Advanced Configuration**

```bash
# Custom output directory and timeout
uv run benchmark run \
  --test-files-dir /path/to/documents \
  --output-dir custom_results \
  --timeout 600 \
  --no-charts

# Performance optimization
uv run benchmark run \
  --test-files-dir sample_documents \
  --frameworks kreuzberg_async \
  --timeout 60
```

### Analyzing Results

#### 1. **Console Output**

Results are displayed in rich tables during execution:

```
Selected frameworks: ['kreuzberg_sync', 'markitdown']
Selected file types: ['pdf', 'html']
Test files directory: sample_documents
Output directory: results

┌──────────────┬───────────┬──────────┬─────────┬─────────┐
│ Framework    │ File Type │ Avg Time │ Memory  │ Success │
│              │           │   (s)    │  (MB)   │  Rate   │
├──────────────┼───────────┼──────────┼─────────┼─────────┤
│ kreuzberg_sy │ html      │   0.01   │  535.6  │ 100.0%  │
│ markitdown   │ html      │   0.01   │  556.3  │ 100.0%  │
└──────────────┴───────────┴──────────┴─────────┴─────────┘
```

#### 2. **File Exports**

Results are automatically saved in multiple formats:

```
results/
�� detailed_results.csv     # Per-file extraction details
�� summary_results.csv      # Aggregated statistics
�� results.json            # Raw results (msgspec format)
�� summaries.json          # Summary statistics (msgspec format)
�� charts/                 # Performance visualizations
    �� extraction_time_comparison.png
    �� memory_usage_comparison.png
    �� success_rate_comparison.png
    �� performance_heatmap.png
```

#### 3. **Generate Reports from Existing Data**

```bash
# Regenerate console table
uv run benchmark report --results-dir results --output-format table

# Export to CSV
uv run benchmark report --results-dir results --output-format csv

# Generate charts only
uv run benchmark report --results-dir results --output-format charts
```

### Custom Test Documents

#### 1. **Directory Structure**

```
your_test_files/
�� documents/
   �� sample.pdf
   �� presentation.pptx
   �� data.xlsx
�� web/
   �� article.html
   �� page.htm
�� text/
    �� readme.md
    �� notes.txt
```

#### 2. **Supported Formats**

- **PDF**: `.pdf` (including image-based PDFs)
- **Office**: `.docx`, `.pptx`, `.xlsx`
- **Web**: `.html`, `.htm`
- **Text**: `.txt`, `.md`

#### 3. **Running Custom Tests**

```bash
uv run benchmark run --test-files-dir your_test_files
```

## Contributing

### Development Setup

```bash
# Install development dependencies
uv sync --dev

# Install pre-commit hooks
uv run pre-commit install --hook-type commit-msg
uv run pre-commit install

# Run tests
uv run pytest

# Format code
uv run ruff format
uv run ruff check --fix
```

### Adding New Frameworks

1. **Create Extractor Class**:

```python
# In python_text_extraction_benchmarks/extractors.py
class NewFrameworkExtractor:
    def extract_text(self, file_path: str) -> str:
        # Implementation here
        return extracted_text
```

1. **Update Framework Enum**:

```python
# In python_text_extraction_benchmarks/types.py
class Framework(str, Enum):
    NEW_FRAMEWORK = "new_framework"
```

1. **Register in Factory**:

```python
# In python_text_extraction_benchmarks/extractors.py
def get_extractor(framework: str):
    extractors = {
        "new_framework": NewFrameworkExtractor,
        # ...
    }
```

### Commit Guidelines

This project uses [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Feature additions
git commit -m "feat: add support for new document format"

# Bug fixes
git commit -m "fix: handle timeout errors gracefully"

# Performance improvements
git commit -m "perf: optimize memory usage in profiler"

# Documentation updates
git commit -m "docs: update installation instructions"
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Kreuzberg**: [@Goldziher](https://github.com/Goldziher) for the comprehensive text extraction library
- **Docling**: IBM Research Deep Search team for advanced document processing
- **MarkItDown**: Microsoft for the lightweight LLM-optimized converter
- **Unstructured**: Unstructured.io team for enterprise-grade document processing

______________________________________________________________________

*Benchmark results may vary based on document complexity, system specifications, and framework versions. These tests were conducted on macOS with CPU-only processing as of January 2025.*
