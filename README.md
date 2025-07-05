# Python Text Extraction Libraries Benchmarks 2025

> **🎯 [📊 VIEW LIVE BENCHMARK RESULTS →](https://goldziher.github.io/python-text-extraction-libs-benchmarks/)**

Automated performance benchmarking of Python text extraction frameworks with real-time updates.

## 🏆 What You'll Find in the Results

- **⚡ Performance Comparison** - Speed, memory usage, and success rates across all frameworks
- **📊 Interactive Charts** - Visual breakdowns by file type, size category, and framework
- **🔍 Detailed Metrics** - Per-file results, error analysis, and resource utilization
- **📈 Trend Analysis** - Performance changes over iterations and time
- **🎯 Framework Recommendations** - Guidance for choosing the right tool

## 🔬 Framework Assessment

### ⚡ **Kreuzberg** (71MB, 20 deps)

**Best for: Production workloads, edge computing, cloud functions**

- Fastest extraction speeds (35+ files/second)
- Both sync and async APIs with OCR support
- **Lightweight**: Perfect for AWS Lambda, edge functions, serverless
- **Smallest footprint**: 71MB with only 20 dependencies
- Handles all document types reliably

### 🏢 **Unstructured** (146MB, 54 deps)

**Best for: Enterprise applications, mixed document types**

- Most reliable overall (88%+ success rate)
- Handles complex layouts well
- Moderate speed, good for batch processing
- **Moderate footprint**: 146MB installation with 54 dependencies

### 📝 **MarkItDown** (251MB, 25 deps)

**Best for: Simple documents, LLM preprocessing**

- Good for basic PDF and Office documents
- **Limitation**: Struggles with large/complex files (>10MB)
- **ONNX Runtime included**: 251MB (includes ML inference models)
- Optimized for Markdown output

### 🔬 **Docling** (1,032MB, 88 deps)

**Best for: Research environments, ML workflows**

- Advanced document understanding with ML models
- **Major limitation**: Extremely slow (often 60+ minutes per file)
- **Frequent failures** on medium-sized documents due to timeouts
- **Heaviest install**: 1GB+ with PyTorch, transformers, vision models

## 📊 Test Coverage

- **94 Documents** - PDFs, Word docs, HTML, images, and more (~210MB total)
- **Real-world Files** - From tiny text files to 59MB academic papers
- **5 Size Categories** - Tiny (\<100KB), Small (100KB-1MB), Medium (1-10MB), Large (10-50MB), Huge (>50MB)
- **Multi-language** - English, Hebrew, German, Chinese, Japanese, Korean
- **CPU-only Processing** - No GPU acceleration for fair comparison
- **Comprehensive Metrics** - Speed, memory usage, success rates, installation sizes

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/Goldziher/python-text-extraction-libs-benchmarks.git
cd python-text-extraction-libs-benchmarks

# Install dependencies
uv sync --all-extras

# Run benchmarks (specific framework and category)
uv run python -m src.cli benchmark --framework kreuzberg_sync --category small

# Generate reports
uv run python -m src.cli report --output-format html
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
│   ├── extractors.py       # Framework implementations
│   ├── visualize.py        # Chart generation
│   └── cli.py             # Command-line interface
├── test_documents/         # 94 test files (~210MB)
├── .github/workflows/      # CI/CD automation
└── CLAUDE.md              # Detailed technical documentation
```

## 🔧 Technical Details

- **Python 3.13+** with modern async/await patterns
- **msgspec** for fast JSON serialization
- **plotly/matplotlib** for comprehensive visualizations
- **GitHub Actions** for automated benchmarking
- **uv** for fast dependency management

## 📊 Performance Highlights

Based on our latest benchmarks:

### 🏆 **Winners by Category**

- **Speed**: Kreuzberg (35+ files/second)
- **Reliability**: Unstructured (88%+ success rate)
- **Installation Size**: Kreuzberg (71MB, 20 deps vs Docling's 1GB+, 88 deps)
- **Enterprise Features**: Unstructured

### ⚠️ **Key Limitations**

- **Docling**: Often fails/times out on medium files (>1MB)
- **MarkItDown**: Struggles with large/complex documents (>10MB)
- **All frameworks**: Performance varies significantly by document type

### 🎯 **Quick Recommendations**

- **High-volume production & edge computing**: Choose Kreuzberg
- **Enterprise/mixed docs**: Choose Unstructured
- **Simple docs for LLMs**: Choose Kreuzberg
- **Research/ML workflows**: Choose Kreuzberg with fallback to Unstructured

See the [live results](https://goldziher.github.io/python-text-extraction-libs-benchmarks/) for detailed comparisons and failure analysis.

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
