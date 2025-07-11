# Python Text Extraction Libraries Benchmarks 2025

[![Benchmark Pipeline](https://github.com/Goldziher/python-text-extraction-libs-benchmarks/actions/workflows/benchmark-by-framework.yml/badge.svg)](https://github.com/Goldziher/python-text-extraction-libs-benchmarks/actions/workflows/benchmark-by-framework.yml)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Frameworks](https://img.shields.io/badge/frameworks-5-green.svg)](#-framework-assessment)
[![Documents](https://img.shields.io/badge/test_documents-94-blue.svg)](#-test-coverage)

> **🎯 [📊 VIEW LIVE BENCHMARK RESULTS →](https://goldziher.github.io/python-text-extraction-libs-benchmarks/)**

Comprehensive automated benchmarking of text extraction frameworks with enhanced CI/CD pipeline and real-time performance monitoring.

## 🏆 What You'll Find in the Results

- **⚡ Performance Comparison** - Speed, memory usage, and success rates across 5 frameworks
- **📊 Interactive Charts** - Visual breakdowns by file type, size category, and framework
- **🔍 Detailed Metrics** - Per-file results, error analysis, and resource utilization
- **📈 Trend Analysis** - Performance changes over iterations and time
- **🎯 Framework Recommendations** - Guidance for choosing the right tool for your use case
- **✨ Quality Assessment** - Extraction quality scores (0-1) measuring completeness, coherence, and accuracy
- **🚀 Latest Addition** - Extractous framework performance data (Rust-based, ultra-fast)

## 🔬 Framework Assessment

### ⚡ **Kreuzberg** (71MB, 20 deps)

**Best for: Production workloads, edge computing, cloud functions**

- Fastest extraction speeds (35+ files/second)
- Both sync and async APIs with OCR support (Tesseract, EasyOCR, PaddleOCR)
- **Lightweight**: Perfect for AWS Lambda, edge functions, serverless
- **Smallest footprint**: 71MB with only 20 dependencies
- **Format limitations**: No email (EML/MSG) or data format (JSON/YAML) support
- **Success rate**: 72.7% on all formats, ~100% on supported formats

### 🦀 **Extractous** (46MB, Rust-based)

**Best for: High-performance applications, speed-critical workloads**

- **Ultra-fast**: 18x faster than traditional Python solutions
- **Rust-based**: Native performance without garbage collection overhead
- **Minimal footprint**: 11x less memory usage than Python alternatives
- Built-in OCR support via Tesseract integration
- **Format support**: 1000+ formats via Apache Tika
- **Success rate**: 94.3% across all test documents

### 🏢 **Unstructured** (146MB, 54 deps)

**Best for: Enterprise applications, mixed document types**

- Most comprehensive format support (64+ formats including emails)
- Handles complex layouts well
- Moderate speed, good for batch processing
- **Moderate footprint**: 146MB installation with 54 dependencies
- **Success rate**: 88.6% across diverse formats

### 📝 **MarkItDown** (251MB, 25 deps)

**Best for: Simple documents, LLM preprocessing**

- Good for basic PDF and Office documents
- **Limitation**: Struggles with large/complex files (>10MB)
- **ONNX Runtime included**: 251MB (includes ML inference models)
- Optimized for Markdown output but slower than Kreuzberg
- **Success rate**: 77.3% with some format limitations

### 🔬 **Docling** (1,032MB, 88 deps)

**Best for: Research environments, ML workflows**

- Advanced document understanding with ML models
- **Major limitation**: Extremely slow (often 60+ minutes per file)
- **Frequent failures** on medium-sized documents due to timeouts
- **Heaviest install**: 1GB+ with PyTorch, transformers, vision models
- **Success rate**: 69.3% (many timeouts on larger files)

## 📊 Test Coverage

- **94 Documents** - PDFs, Word docs, HTML, images, and more (~210MB total)
- **Real-world Files** - From tiny text files to 59MB academic papers
- **5 Size Categories** - Tiny (\<100KB), Small (100KB-1MB), Medium (1-10MB), Large (10-50MB), Huge (>50MB)
- **Multi-language** - English, Hebrew, German, Chinese, Japanese, Korean
- **CPU-only Processing** - No GPU acceleration for fair comparison
- **5 Frameworks** - Kreuzberg, Extractous, Unstructured, MarkItDown, Docling
- **Enhanced CI/CD** - 2-hour timeout handling with graceful failure management
- **Comprehensive Metrics** - Speed, memory usage, success rates, installation sizes

## 📋 Format Support Analysis

Our comprehensive testing revealed significant differences in format support across frameworks:

### 🎯 Format Support Tiers

#### **Tier 1: Universal Support** (5/5 frameworks)

These 7 formats are supported by ALL frameworks:

- `.pdf` - Portable Document Format
- `.pptx` - PowerPoint presentations
- `.xlsx` - Excel spreadsheets
- `.png` - Portable Network Graphics
- `.bmp` - Bitmap images
- `.html` - Web pages
- `.csv` - Comma-separated values

#### **Tier 2: Common Support** (4/5 frameworks)

These 4 additional formats work with most frameworks:

- `.xls` - Legacy Excel (not Docling)
- `.md` - Markdown (not MarkItDown, ironically)
- `.jpeg` - JPEG images (not Unstructured)
- `.txt` - Plain text (not Docling)

### 📊 Framework-Specific Capabilities

| Framework        | Supported Formats             | Notable Exclusions    |
| ---------------- | ----------------------------- | --------------------- |
| **Extractous**   | 1000+ formats via Apache Tika | Some edge cases       |
| **Unstructured** | 64+ formats including emails  | Few limitations       |
| **MarkItDown**   | Common office & web formats   | `.docx`, `.md` issues |
| **Kreuzberg**    | 14/18 tested formats          | No email/JSON/YAML    |
| **Docling**      | 10/18 tested formats          | Limited coverage      |

### 🔄 Tiered Benchmarking Options

Choose the appropriate tier based on your needs:

```bash
# Tier 1: Test only universal formats (7 formats, 100% framework support)
uv run python -m src.cli benchmark --framework all --format-tier universal

# Tier 2: Test common formats (11 formats, 80%+ framework support) - RECOMMENDED
uv run python -m src.cli benchmark --framework all --format-tier common

# Test all formats (18 formats, shows full capabilities)
uv run python -m src.cli benchmark --framework all --format-tier all
```

For detailed format compatibility, see [FRAMEWORK_FORMAT_SUPPORT.md](FRAMEWORK_FORMAT_SUPPORT.md)

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/Goldziher/python-text-extraction-libs-benchmarks.git
cd python-text-extraction-libs-benchmarks

# Install dependencies (fast with uv)
uv sync --all-extras

# List available frameworks
uv run python -m src.cli list-frameworks

# Run benchmarks - NEW: Extractous framework
uv run python -m src.cli benchmark --framework extractous --category small

# Compare multiple frameworks
uv run python -m src.cli benchmark --framework kreuzberg_sync,extractous --category tiny,small

# Fair comparison mode - test only universally supported formats
uv run python -m src.cli benchmark --framework all --format-tier universal

# Real-world scenario - test commonly supported formats (recommended)
uv run python -m src.cli benchmark --framework all --format-tier common

# Generate comprehensive reports
uv run python -m src.cli report --output-format html
uv run python -m src.cli visualize --output-dir charts/
```

## 🔬 Benchmarking Methodology

### Extraction Quality & Reliability Metrics

This benchmark suite measures both **performance** and **extraction quality/reliability** to provide a comprehensive evaluation:

#### 📊 **Quality Assessment Metrics** (0-1 scale)

1. **Extraction Completeness** (25% weight)

    - Estimates how much content was successfully extracted
    - Detects missing sections, truncated text, or incomplete parsing
    - Compares against expected document characteristics

1. **Text Coherence** (20% weight)

    - Measures logical flow and readability of extracted text
    - Detects garbled text, encoding issues, or structural problems
    - Evaluates sentence and paragraph structure preservation

1. **Noise Ratio** (10% negative weight)

    - Identifies extraction artifacts, repeated characters, or garbage text
    - Detects OCR errors and encoding problems
    - Lower noise = higher quality score

1. **Format Preservation** (15% weight)

    - Document-specific quality checks:
        - **PDFs**: Proper text encoding, no OCR artifacts
        - **Office docs**: Structure preservation, no metadata pollution
        - **HTML**: Clean text without tags or script remnants
    - Table and list structure integrity

1. **Readability Metrics** (10% weight)

    - Flesch Reading Ease score
    - Gunning Fog Index
    - Indicates if extracted text maintains original readability

1. **Semantic Similarity** (20% weight, when reference available)

    - Compares extracted text against known-good reference extractions
    - Uses sentence transformers for meaning preservation
    - TF-IDF and Jaccard similarity for content coverage

#### 🎯 **Reliability Metrics**

- **Success Rate**: Percentage of files extracted without errors
- **Timeout Rate**: Files that exceed processing time limits
- **Error Analysis**: Categorized failure reasons (parsing, memory, timeout)
- **Consistency**: Variance across multiple extraction attempts

### Performance Benchmarking

Each framework is evaluated across:

- **Speed**: Extraction time per file and throughput (files/second)
- **Memory Usage**: Peak RSS and average consumption
- **CPU Utilization**: Processing efficiency
- **Scalability**: Performance across different file sizes (tiny to huge)

### Test Methodology

1. **Diverse Document Set**: 94 real-world documents (~210MB)

    - Multiple formats: PDF, DOCX, HTML, images, etc.
    - Various sizes: From 1KB to 59MB
    - Multiple languages: English, Hebrew, German, Chinese, Japanese, Korean
    - Special cases: OCR-required images, complex layouts, tables

1. **Fair Comparison**:

    - CPU-only processing (no GPU acceleration)
    - Cold-start performance (no warmup runs)
    - Cache cleared between framework runs
    - Isolated CI jobs to prevent interference

1. **Statistical Rigor**:

    - Multiple iterations per document (default: 3)
    - Median values for performance metrics
    - Standard deviation tracking
    - Outlier detection and handling

### Running Quality Assessment

```bash
# Add quality metrics to existing benchmark results
uv run python -m src.cli quality-assess \
  --results-file results/results.json \
  --output-file results/enhanced_results.json

# Compare against reference extractions
uv run python -m src.cli quality-assess \
  --results-file results/results.json \
  --reference-dir reference_texts/ \
  --output-file results/quality_enhanced.json
```

## 📖 Documentation

### Core Commands

```bash
# List available frameworks
uv run python -m src.cli list-frameworks

# Run comprehensive benchmarks
uv run python -m src.cli benchmark --framework all --category tiny,small

# Aggregate multiple benchmark runs
uv run python -m src.cli aggregate results/ --output-dir aggregated/

# Generate visualizations
uv run python -m src.cli visualize --aggregated-file results.json
```

### Configuration

The benchmark suite automatically detects document languages and configures frameworks accordingly. See `CLAUDE.md` for detailed configuration options and framework-specific settings.

## 🤝 Contributing

1. **Add New Frameworks** - Implement the extractor interface in `src/extractors.py`
1. **Improve Tests** - Add test documents to `test_documents/`
1. **Enhance Visualizations** - Modify `src/visualize.py` for new chart types
1. **Report Issues** - Use GitHub Issues for bugs and feature requests

## 📋 Project Structure

```
python-text-extraction-libs-benchmarks-2025/
├── src/                    # Main source code
│   ├── benchmark.py        # Core benchmarking engine
│   ├── extractors.py       # Framework implementations (now with Extractous!)
│   ├── profiler.py         # Performance profiling system
│   ├── visualize.py        # Chart generation
│   ├── reporting.py        # Results analysis
│   └── cli.py             # Command-line interface
├── test_documents/         # 94 test files (~210MB)
│   ├── pdfs/              # 24 PDF files (17KB - 59MB)
│   ├── office/            # 35 Office documents
│   ├── images/            # 11 image files for OCR
│   └── ...                # HTML, markdown, text files
├── .github/workflows/      # Enhanced CI/CD automation
│   └── benchmark-by-framework.yml  # Improved timeout handling
└── CLAUDE.md              # Detailed technical documentation
```

## 🔧 Technical Details

- **Python 3.13+** with modern async/await patterns
- **Rust Integration**: Extractous provides native Rust performance
- **Enhanced CI/CD**: 2-hour timeout handling with graceful failure management
- **msgspec** for fast JSON serialization
- **plotly/matplotlib** for comprehensive visualizations
- **GitHub Actions** for automated benchmarking with isolated framework jobs
- **uv** for fast dependency management

## 🆕 Recent Improvements (v1.3.0)

### 📋 **Format Support Analysis**

- **Tiered Format Support**: Introduced 2-tier system (Universal, Common)
- **Flexible Benchmarking**: Added `--format-tier` option (universal, common, all)
- **Comprehensive Testing**: Analyzed format support across all 18 file types
- **Format Documentation**: Created detailed compatibility matrix in FRAMEWORK_FORMAT_SUPPORT.md
- **Success Rate Correction**: Fixed misleading metrics when frameworks skip categories

### 🚀 **New Framework Addition**

- **Extractous Integration**: Added ultra-fast Rust-based framework
- **Performance Boost**: 18x faster than traditional Python solutions
- **Memory Efficiency**: 11x less memory usage
- **OCR Support**: Built-in Tesseract integration with language detection

### 🛠️ **Enhanced CI/CD Pipeline**

- **Timeout Handling**: 2-hour timeouts with graceful failure management
- **Robust Aggregation**: Runs even when some frameworks fail/timeout
- **Failure Reporting**: Comprehensive timeout and error analysis
- **Isolated Jobs**: Each framework runs independently for better reliability
- **System Dependencies**: Auto-install Pandoc, Tesseract with all language packs

### 📊 **Improved Benchmarking**

- **Memory Profiling**: Enhanced resource monitoring with 50ms sampling
- **Quality Metrics**: Better extraction quality assessment
- **Performance Tracking**: More accurate CPU and memory measurements
- **Fair Success Rates**: Count skipped files as failures for honest comparison

## 📊 Performance Highlights

Based on our latest benchmarks:

### 🏆 **Winners by Category**

- **🚀 Speed**: Extractous (18x faster than Python solutions) → Kreuzberg (35+ files/second)
- **🛡️ Reliability**: Extractous (94.3%) → Unstructured (88.6%) across all formats
- **📋 Format Support**: Unstructured (64+ formats) → Extractous (1000+ via Tika)
- **💾 Memory Footprint**: Extractous (11x less memory) → Kreuzberg (~530MB on average)
- **📦 Installation Size**: Extractous (46MB, Rust-based) → Kreuzberg (71MB, 20 deps)
- **🏢 Enterprise Features**: Unstructured (emails, complex layouts)
- **⚖️ Fair Comparison**: When testing only universal formats, all frameworks achieve >95% success

### ⚠️ **Key Limitations**

- **Docling**: Often fails/times out on medium files (>1MB), slow for smaller files
- **MarkItDown**: Struggles with large/complex documents (>10MB)
- **Performance varies**: Significant differences by document type and complexity

### 🎯 **Quick Recommendations**

- **🚀 Maximum performance**: Choose **Extractous** (new Rust-based framework)
- **⚡ High-volume production**: Choose **Kreuzberg** (fast, lightweight)
- **🏢 Enterprise/mixed docs**: Choose **Unstructured** (most reliable)
- **🤖 LLM preprocessing**: Choose **Extractous** or **Kreuzberg**
- **🔬 Research/ML workflows**: Choose **Extractous** with fallback to **Kreuzberg**

See the [live results](https://goldziher.github.io/python-text-extraction-libs-benchmarks/) for detailed comparisons and failure analysis.

> **📊 Active Benchmarking**: v1.2.0 benchmark pipeline is currently running with the new Extractous framework! Results will be available shortly at the live dashboard.

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Framework maintainers for building excellent tools
- Contributors who added test documents and improvements
- The Python community for feedback and suggestions

______________________________________________________________________

**🔗 Links:**

- [📊 Live Results Dashboard](https://goldziher.github.io/python-text-extraction-libs-benchmarks/)
- [⚙️ GitHub Actions](https://github.com/Goldziher/python-text-extraction-libs-benchmarks/actions)
- [📖 Technical Documentation](CLAUDE.md)
