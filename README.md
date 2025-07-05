# Python Text Extraction Libraries Benchmarks 2025

> **🎯 [📊 VIEW LIVE BENCHMARK RESULTS →](https://goldziher.github.io/python-text-extraction-libs-benchmarks/)**

Automated performance benchmarking of Python text extraction frameworks with real-time updates.

## 🏆 What You'll Find in the Results

- **⚡ Performance Comparison** - Speed, memory usage, and success rates across all frameworks
- **📊 Interactive Charts** - Visual breakdowns by file type, size category, and framework
- **🔍 Detailed Metrics** - Per-file results, error analysis, and resource utilization
- **📈 Trend Analysis** - Performance changes over iterations and time
- **🎯 Framework Recommendations** - Guidance for choosing the right tool

## 🔬 Tested Frameworks

### Speed Champions
- **Kreuzberg** (sync/async) - Lightning fast with OCR capabilities
- **MarkItDown** - Microsoft's lightweight converter

### Quality Leaders  
- **Unstructured** - Enterprise-grade reliability
- **Docling** - IBM's research-backed solution

## 📊 Test Coverage

- **1,000+ Documents** - PDFs, Word docs, HTML, images, and more
- **Real-world Files** - From tiny text files to 59MB academic papers
- **Multi-language** - English, Hebrew, German, Chinese, Japanese, Korean
- **CPU-only Processing** - No GPU acceleration for fair comparison

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
2. **Improve Tests** - Add test documents to `test_documents/`
3. **Enhance Visualizations** - Modify `src/visualize.py` for new chart types
4. **Report Issues** - Use GitHub Issues for bugs and feature requests

## 📋 Project Structure

```
python-text-extraction-libs-benchmarks-2025/
├── src/                    # Main source code
│   ├── benchmark.py        # Core benchmarking engine
│   ├── extractors.py       # Framework implementations
│   ├── visualize.py        # Chart generation
│   └── cli.py             # Command-line interface
├── test_documents/         # 1000+ test files
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

- **Fastest**: Kreuzberg (35+ files/second)
- **Most Reliable**: Unstructured (88%+ success rate)
- **Best Balance**: Framework choice depends on your specific use case

See the [live results](https://goldziher.github.io/python-text-extraction-libs-benchmarks/) for detailed comparisons.

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Framework maintainers for building excellent tools
- Contributors who added test documents and improvements
- The Python community for feedback and suggestions

---

**🔗 Links:**
- [📊 Live Results Dashboard](https://goldziher.github.io/python-text-extraction-libs-benchmarks/)
- [⚙️ GitHub Actions](https://github.com/Goldziher/python-text-extraction-libs-benchmarks/actions)
- [📖 Technical Documentation](CLAUDE.md)