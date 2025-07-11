# Framework Format Support Matrix

## Overview

This document provides a comprehensive analysis of file format support across all tested text extraction frameworks based on benchmark results and official documentation.

## Tested File Formats

The benchmark suite tests 18 unique file formats across 94 documents:

| Category   | Formats                                           | Count |
| ---------- | ------------------------------------------------- | ----- |
| Documents  | `.pdf`, `.docx`, `.pptx`, `.xlsx`, `.xls`, `.odt` | 59    |
| Web/Markup | `.html`, `.md`, `.rst`, `.org`                    | 24    |
| Images     | `.jpg`, `.jpeg`, `.png`, `.bmp`                   | 11    |
| Email      | `.eml`, `.msg`                                    | 5     |
| Data       | `.csv`, `.json`, `.yaml`                          | 4     |
| Text       | `.txt`                                            | 3     |

## Framework Support Matrix

Based on benchmark results and failure analysis:

| Format  | Kreuzberg | Docling | MarkItDown | Unstructured | Extractous |
| ------- | --------- | ------- | ---------- | ------------ | ---------- |
| `.pdf`  | ✅        | ✅      | ✅         | ✅           | ✅         |
| `.docx` | ❌\*      | ✅      | ❌         | ✅           | ❌\*       |
| `.pptx` | ✅        | ✅      | ✅         | ✅           | ✅         |
| `.xlsx` | ✅        | ✅      | ✅         | ✅           | ✅         |
| `.xls`  | ✅        | ❌      | ✅         | ✅           | ✅         |
| `.odt`  | ❌\*      | ❌      | ❌         | ❌           | ✅         |
| `.html` | ✅        | ✅      | ✅         | ✅           | ✅         |
| `.md`   | ✅        | ✅      | ❌         | ✅           | ✅         |
| `.rst`  | ❌\*      | ❌      | ✅         | ❌           | ✅         |
| `.org`  | ❌\*      | ❌      | ✅         | ❌           | ✅         |
| `.jpg`  | ✅        | ✅      | ✅         | ❌           | ❌         |
| `.jpeg` | ✅        | ✅      | ✅         | ❌           | ✅         |
| `.png`  | ✅        | ✅      | ✅         | ✅           | ✅         |
| `.bmp`  | ✅        | ✅      | ✅         | ✅           | ✅         |
| `.eml`  | ❌        | ❌      | ✅         | ✅           | ✅         |
| `.msg`  | ❌        | ❌      | ✅         | ✅           | ✅         |
| `.csv`  | ✅        | ✅      | ✅         | ✅           | ✅         |
| `.json` | ❌        | ❌      | ✅         | ✅           | ✅         |
| `.yaml` | ❌        | ❌      | ✅         | ✅           | ✅         |
| `.txt`  | ✅        | ❌      | ✅         | ✅           | ✅         |

\*Note: Failures may be due to missing system dependencies (e.g., Pandoc for .docx in Kreuzberg)

## Format Support Tiers

### Tier 1: Universal Support (5/5 frameworks)

These **7 formats** are reliably supported by ALL frameworks:

- `.pdf` - Portable Document Format
- `.pptx` - PowerPoint presentations
- `.xlsx` - Excel spreadsheets
- `.png` - Portable Network Graphics
- `.bmp` - Bitmap images
- `.html` - Web pages
- `.csv` - Comma-separated values

### Tier 2: Common Support (4/5 frameworks)

These **4 additional formats** work with most frameworks:

- `.xls` - Legacy Excel (not supported by Docling)
- `.md` - Markdown (not supported by MarkItDown, ironically)
- `.jpeg` - JPEG images (not supported by Unstructured)
- `.txt` - Plain text (not supported by Docling)

## Framework-Specific Analysis

### Kreuzberg (v3.5.0+)

- **Strengths**: Fast processing, excellent PDF support, good OCR integration
- **Limitations**:
    - No email format support (by design)
    - No structured data format support (JSON/YAML)
    - Requires Pandoc for some document formats
- **Success Rate**: 72.7% (with missing dependencies)

### Docling (v2.15.0+)

- **Strengths**: Advanced ML-based document understanding, excellent table extraction
- **Limitations**:
    - Very slow (60+ minutes per file common)
    - Limited format support compared to others
    - Huge installation size (1GB+)
- **Success Rate**: 69.3% (including timeouts)

### MarkItDown (v0.0.1a2+)

- **Strengths**: Lightweight, good markdown conversion
- **Limitations**:
    - Struggles with large files
    - Inconsistent document format support
- **Success Rate**: 77.3%

### Unstructured (v0.16.11+)

- **Strengths**: Most comprehensive format support (64+ formats)
- **Limitations**:
    - Moderate speed
    - Complex dependency management
- **Success Rate**: 88.6%

### Extractous (v0.1.0+)

- **Strengths**:
    - Fastest performance (18x faster than others)
    - Supports 1000+ formats via Apache Tika
    - Minimal memory footprint
- **Limitations**:
    - Some specific format issues in current version
- **Success Rate**: 94.3%

## Recommendations

### Benchmarking Strategy

1. **For Fair Performance Comparison** (Tier 1)

    - Use `--format-tier universal` to test only the 7 universally supported formats
    - All frameworks will achieve near 100% success rates
    - Best for comparing raw performance metrics

1. **For Real-World Scenarios** (Tier 2) - **RECOMMENDED**

    - Use `--format-tier common` to test 11 commonly supported formats
    - Represents typical business document processing needs
    - Balances fairness with practical coverage

1. **For Complete Coverage** (All formats)

    - Use `--format-tier all` or omit the flag
    - Tests all 18 format types
    - Best for understanding full framework capabilities
    - Shows specialized format support (email, data formats)

### By Use Case

- **Email Processing**: Use Unstructured or Extractous
- **Speed Critical**: Use Extractous or Kreuzberg
- **Document Understanding**: Use Docling (if time permits)
- **Simple Conversion**: Use MarkItDown
- **Maximum Coverage**: Use Unstructured

## Technical Notes

1. **OCR Support**: All frameworks support OCR but with different backends:

    - Kreuzberg: Tesseract, EasyOCR, PaddleOCR
    - Docling: Built-in ML models
    - MarkItDown: ONNX Runtime
    - Unstructured: Tesseract
    - Extractous: Tesseract

1. **System Dependencies**:

    - Kreuzberg: Requires Pandoc for some formats
    - All: Benefit from Tesseract for OCR
    - Some: Require poppler-utils for PDF processing

1. **Performance Characteristics**:

    - Extractous: ~18x faster than traditional Python solutions
    - Kreuzberg: 35+ files/second on small documents
    - Docling: Can take hours for complex PDFs
    - Memory usage varies from 71MB (Kreuzberg) to 1GB+ (Docling)
