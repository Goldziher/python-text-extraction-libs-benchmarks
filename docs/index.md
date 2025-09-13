# Python Text Extraction Libraries Benchmarks 2025

Welcome to the comprehensive performance analysis of Python text extraction frameworks. This benchmark suite evaluates the leading libraries for extracting text from documents, images, and various file formats.

## 🎯 Quick Results

!!! info "Latest Benchmark Results"

    **6 frameworks tested** across **94 documents** in **18 file formats**

    **Top Performers:**

    - **Speed**: Kreuzberg (15.7 files/sec)
    - **Memory**: Kreuzberg Async (259MB avg)
    - **Compatibility**: Unstructured (97.2% success)
    - **Quality**: Docling (ML-powered understanding)

## 🏆 Framework Rankings

| Framework        | Speed      | Success Rate | Memory Usage | Installation |
| ---------------- | ---------- | ------------ | ------------ | ------------ |
| **Kreuzberg**    | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐   | ⭐⭐⭐⭐⭐   | 71MB         |
| **MarkItDown**   | ⭐⭐⭐⭐   | ⭐⭐⭐⭐     | ⭐⭐⭐⭐     | 251MB        |
| **Extractous**   | ⭐⭐⭐     | ⭐⭐⭐⭐⭐   | ⭐⭐⭐⭐     | ~100MB       |
| **Unstructured** | ⭐⭐       | ⭐⭐⭐⭐⭐   | ⭐⭐         | 146MB        |
| **Docling**      | ⭐         | ⭐⭐⭐⭐⭐   | ⭐           | 1GB+         |

## 📊 Performance Highlights

![Performance Overview](../charts/performance_comparison_large.png)

### Key Metrics

=== "Speed Performance"

    - **Kreuzberg Sync**: 15.66 files/second
    - **MarkItDown**: 13.22 files/second
    - **Extractous**: 2.59 files/second
    - **Unstructured**: 2.19 files/second
    - **Docling**: 0.16 files/second

=== "Memory Efficiency"

    - **Kreuzberg Async**: 0.0 MB average
    - **Kreuzberg Sync**: 259.8 MB average
    - **MarkItDown**: 263.7 MB average
    - **Extractous**: 410.0 MB average
    - **Unstructured**: 1,375.1 MB average
    - **Docling**: 1,749.6 MB average

=== "Success Rates"

    - **Kreuzberg**: 100%\* (supported formats)
    - **Extractous**: 98.6%
    - **Docling**: 98.1%
    - **MarkItDown**: 97.8%
    - **Unstructured**: 97.2%

## 🔍 What's Tested

### Document Formats

- **PDF**: Complex layouts, tables, images
- **Office**: DOCX, PPTX, XLSX, XLS, ODT
- **Images**: PNG, JPG, JPEG, BMP with OCR
- **Web**: HTML, Markdown, reStructuredText
- **Data**: CSV, JSON, YAML
- **Email**: EML, MSG formats

### Test Categories

- **Tiny**: \<100KB (quick processing)
- **Small**: 100KB-1MB (typical documents)
- **Medium**: 1-10MB (complex documents)
- **Large**: 10-50MB (heavy processing)
- **Huge**: >50MB (stress testing)

## 📈 Interactive Analysis

Explore the complete results:

[Open Interactive Dashboard :material-chart-line:](reports/dashboard.md){ .md-button .md-button--primary }
[View Raw Data :material-database:](reports/data.md){ .md-button }

## 🚀 Getting Started

Choose a framework based on your needs:

=== "Speed Priority"

    **Kreuzberg** offers the fastest processing with efficient resource usage.

    ```bash
    pip install kreuzberg
    ```

=== "Format Coverage"

    **Unstructured** supports the widest range of formats and use cases.

    ```bash
    pip install unstructured
    ```

=== "ML Understanding"

    **Docling** provides advanced document understanding with ML models.

    ```bash
    pip install docling
    ```

=== "Rust Performance"

    **Extractous** delivers native performance with Python bindings.

    ```bash
    pip install extractous
    ```

## 📋 Methodology

This benchmark suite runs on:

- **Python 3.13** on macOS/Linux
- **Real-world documents** (94 files, ~210MB)
- **Cold-start performance** (no warmup)
- **Resource monitoring** (CPU, memory, timing)
- **Multiple iterations** for statistical accuracy

[Learn More About Our Testing :material-flask:](methodology/index.md){ .md-button }

______________________________________________________________________

!!! tip "Framework Recommendations"

    - **Kreuzberg**: Best overall performance and efficiency
    - **MarkItDown**: LLM-optimized Markdown output
    - **Unstructured**: Enterprise-grade format support
    - **Extractous**: Native speed with broad compatibility
    - **Docling**: Advanced ML document understanding

*Last updated: {{ git.date.strftime("%Y-%m-%d") }}*
