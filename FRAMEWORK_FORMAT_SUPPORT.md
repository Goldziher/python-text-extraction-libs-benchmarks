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

## Common Format Subset (All Frameworks Support)

Only **5 formats** are reliably supported by ALL frameworks:

- `.pdf`
- `.pptx`
- `.xlsx`
- `.png`
- `.bmp`

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

### For Maximum Compatibility Testing

Test only these 5 formats that all frameworks support:

- `.pdf`, `.pptx`, `.xlsx`, `.png`, `.bmp`

### For Real-World Benchmarking

Include the most common business formats:

- `.pdf`, `.docx`, `.pptx`, `.xlsx`, `.html`, `.png`

Note: Some frameworks may need additional system dependencies installed.

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
