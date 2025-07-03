# Kreuzberg Testing Guide

This guide provides detailed instructions for running Kreuzberg-specific test suites and performance benchmarks.

## Table of Contents

1. [Quick Start](#quick-start)
1. [Test Configurations](#test-configurations)
1. [Running Benchmarks](#running-benchmarks)
1. [Performance Testing](#performance-testing)
1. [OCR Backend Testing](#ocr-backend-testing)
1. [Language Testing](#language-testing)
1. [Analyzing Results](#analyzing-results)
1. [Troubleshooting](#troubleshooting)

## Quick Start

### Basic Kreuzberg Test

```bash
# Test default Kreuzberg configuration
uv run python -m src.cli benchmark --framework kreuzberg_sync --category tiny --iterations 1

# Test optimized Tesseract configuration
uv run python -m src.cli benchmark --framework kreuzberg_tesseract --category tiny --iterations 1
```

### Compare All Kreuzberg Configurations

```bash
# Clear cache for fair comparison
rm -rf .kreuzberg

# Run comprehensive comparison
uv run python -m src.cli benchmark \
    --framework kreuzberg_sync,kreuzberg_async,kreuzberg_tesseract \
    --category small \
    --iterations 2 \
    --timeout 300
```

## Test Configurations

### Available Kreuzberg Frameworks

| Framework             | Description          | Mode  | OCR Backend |
| --------------------- | -------------------- | ----- | ----------- |
| `kreuzberg_sync`      | Default synchronous  | Sync  | Auto-detect |
| `kreuzberg_async`     | Default asynchronous | Async | Auto-detect |
| `kreuzberg_tesseract` | Optimized Tesseract  | Sync  | Tesseract   |
| `kreuzberg_easyocr`   | EasyOCR backend      | Async | EasyOCR     |
| `kreuzberg_paddleocr` | PaddleOCR backend    | Async | PaddleOCR   |

### Document Categories

| Category | Size Range  | File Count | Best For            |
| -------- | ----------- | ---------- | ------------------- |
| `tiny`   | < 100KB     | 50         | Quick tests         |
| `small`  | 100KB - 1MB | 54         | Standard testing    |
| `medium` | 1MB - 10MB  | 12         | Performance testing |
| `images` | Various     | 7          | OCR testing         |

## Running Benchmarks

### 1. Basic Performance Test

```bash
# Test extraction speed on small documents
uv run python -m src.cli benchmark \
    --framework kreuzberg_tesseract \
    --category small \
    --iterations 3 \
    --output-dir kreuzberg_results
```

### 2. OCR Performance Test

```bash
# Test OCR backends on image files
uv run python -m src.cli benchmark \
    --framework kreuzberg_sync,kreuzberg_tesseract,kreuzberg_easyocr,kreuzberg_paddleocr \
    --category images \
    --iterations 2 \
    --timeout 300
```

### 3. Cache Impact Test

```bash
# First run - cold cache
rm -rf .kreuzberg
uv run python -m src.cli benchmark \
    --framework kreuzberg_sync \
    --category tiny \
    --iterations 1 \
    --output-dir cold_cache_results

# Second run - warm cache
uv run python -m src.cli benchmark \
    --framework kreuzberg_sync \
    --category tiny \
    --iterations 1 \
    --output-dir warm_cache_results
```

### 4. Language-Specific Test

```bash
# Test on multilingual documents
uv run python -m src.cli benchmark \
    --framework kreuzberg_tesseract \
    --test-files-dir test_documents \
    --file-types html \
    --iterations 1
```

## Performance Testing

### Comprehensive Performance Suite

```bash
#!/bin/bash
# comprehensive_kreuzberg_test.sh

echo "=== Kreuzberg Comprehensive Performance Test ==="

# Clear any existing cache
rm -rf .kreuzberg

# Test 1: Compare sync vs async
echo -e "\n1. Testing Sync vs Async..."
uv run python -m src.cli benchmark \
    --framework kreuzberg_sync,kreuzberg_async \
    --category tiny \
    --iterations 3 \
    --output-dir sync_vs_async

# Test 2: Compare OCR backends
echo -e "\n2. Testing OCR Backends..."
uv run python -m src.cli benchmark \
    --framework kreuzberg_tesseract \
    --category images \
    --iterations 2 \
    --output-dir ocr_comparison

# Test 3: Test on different file types
echo -e "\n3. Testing File Type Performance..."
for file_type in pdf docx html; do
    echo "Testing $file_type files..."
    uv run python -m src.cli benchmark \
        --framework kreuzberg_tesseract \
        --file-types $file_type \
        --iterations 1 \
        --output-dir "results_${file_type}"
done

# Test 4: Memory usage test
echo -e "\n4. Testing Memory Usage..."
uv run python -m src.cli benchmark \
    --framework kreuzberg_sync,kreuzberg_tesseract \
    --category medium \
    --iterations 1 \
    --output-dir memory_test

echo -e "\n=== Tests Complete ==="
```

### Speed Comparison Test

```python
# speed_test.py
import time
from pathlib import Path
from src.extractors import KreuzbergSyncExtractor, KreuzbergTesseractExtractor

# Test files
test_files = [
    "test_documents/pdfs/fake-memo.pdf",
    "test_documents/images/example.jpg",
    "test_documents/office/fake.docx"
]

# Test each configuration
for extractor_class, name in [
    (KreuzbergSyncExtractor, "Default Sync"),
    (KreuzbergTesseractExtractor, "Optimized Tesseract")
]:
    print(f"\n{name}:")
    extractor = extractor_class()

    for file_path in test_files:
        start = time.time()
        try:
            text = extractor.extract_text(file_path)
            elapsed = time.time() - start
            print(f"  {Path(file_path).name}: {elapsed:.4f}s ({len(text)} chars)")
        except Exception as e:
            print(f"  {Path(file_path).name}: ERROR - {e}")
```

## OCR Backend Testing

### Installing OCR Backends

```bash
# Install EasyOCR support
uv pip install "kreuzberg[easyocr]"

# Install PaddleOCR support
uv pip install paddlepaddle paddleocr

# Or install all backends
uv sync --extra ocr
```

### Testing EasyOCR

```python
# test_easyocr.py
import asyncio
from src.extractors import KreuzbergEasyOCRExtractor

async def test_easyocr():
    extractor = KreuzbergEasyOCRExtractor()

    # Test on different language images
    test_files = [
        "test_documents/images/example.jpg",  # English
        "test_documents/images/chi_sim_image.jpeg",  # Chinese
        "test_documents/images/jpn-vert.jpeg"  # Japanese
    ]

    for file_path in test_files:
        try:
            text = await extractor.extract_text(file_path)
            print(f"{file_path}: {len(text)} chars extracted")
        except Exception as e:
            print(f"{file_path}: ERROR - {e}")

asyncio.run(test_easyocr())
```

### Testing PaddleOCR

```python
# test_paddleocr.py
import asyncio
from src.extractors import KreuzbergPaddleOCRExtractor

async def test_paddleocr():
    extractor = KreuzbergPaddleOCRExtractor()

    # Test on Asian language documents
    test_files = [
        "test_documents/images/chi_sim_image.jpeg",  # Chinese
        "test_documents/images/jpn-vert.jpeg",  # Japanese
        "test_documents/images/english-and-korean.png"  # Korean
    ]

    for file_path in test_files:
        try:
            text = await extractor.extract_text(file_path)
            print(f"{file_path}: {len(text)} chars extracted")
        except Exception as e:
            print(f"{file_path}: ERROR - {e}")

asyncio.run(test_paddleocr())
```

## Language Testing

### Test Language Detection

```python
# test_language_detection.py
from src.extractors import get_language_config

test_files = [
    "Israel_Hebrew.html",
    "Germany_German.html",
    "China_Chinese.html",
    "jpn-vert.jpeg",
    "english-and-korean.png",
    "regular_document.pdf"
]

for filename in test_files:
    lang = get_language_config(filename)
    print(f"{filename}: detected language = {lang}")
```

### Test Multi-Language Documents

```bash
# Test Hebrew documents
uv run python -m src.cli benchmark \
    --framework kreuzberg_tesseract \
    --test-files-dir test_documents/html \
    --iterations 1 \
    --output-dir hebrew_test \
    | grep -E "(Hebrew|הע)"

# Test Asian language documents
uv run python -m src.cli benchmark \
    --framework kreuzberg_tesseract \
    --test-files-dir test_documents/images \
    --iterations 1 \
    --output-dir asian_lang_test
```

## Analyzing Results

### Generate Performance Report

```python
# analyze_results.py
import json
import pandas as pd
from pathlib import Path

def analyze_kreuzberg_results(results_dir="results"):
    # Load results
    with open(f"{results_dir}/benchmark_summaries.json") as f:
        summaries = json.load(f)

    # Filter Kreuzberg results
    kreuzberg_results = [s for s in summaries if "kreuzberg" in s["framework"]]

    # Create comparison table
    df = pd.DataFrame(kreuzberg_results)
    df = df[["framework", "success_rate", "avg_extraction_time", "files_per_second"]]

    print("Kreuzberg Performance Comparison:")
    print(df.to_string(index=False))

    # Calculate speedups
    if len(kreuzberg_results) > 1:
        base_time = kreuzberg_results[0]["avg_extraction_time"]
        print("\nSpeedup Analysis:")
        for result in kreuzberg_results[1:]:
            speedup = base_time / result["avg_extraction_time"]
            print(f"{result['framework']}: {speedup:.1f}x faster than {kreuzberg_results[0]['framework']}")

analyze_kreuzberg_results()
```

### Visualize Performance

```bash
# Generate performance charts
uv run python -m src.cli report \
    --results-dir results \
    --output-format charts

# Generate detailed CSV report
uv run python -m src.cli report \
    --results-dir results \
    --output-format csv
```

## Troubleshooting

### Common Issues

#### 1. OCR Backend Not Found

```
Error: MissingDependencyError: The package 'paddleocr' is not installed
```

**Solution:**

```bash
uv pip install paddlepaddle paddleocr
```

#### 2. Language Model Missing

```
Error: Tesseract couldn't find language data for 'chi_sim'
```

**Solution:**

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr-chi-sim

# macOS
brew install tesseract-lang
```

#### 3. Async Extractor in Sync Context

```
Error: NotImplementedError: Sync OCR not implemented for easyocr
```

**Solution:** Use async context or switch to Tesseract backend:

```python
# Use async
import asyncio
result = asyncio.run(extractor.extract_text(file_path))

# Or use Tesseract
extractor = KreuzbergTesseractExtractor()
```

#### 4. Cache Affecting Results

**Solution:** Clear cache before benchmarking:

```bash
rm -rf .kreuzberg
```

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run extraction with debug output
extractor = KreuzbergTesseractExtractor()
result = extractor.extract_text("document.pdf")
```

### Performance Profiling

```python
# profile_kreuzberg.py
import cProfile
import pstats
from src.extractors import KreuzbergTesseractExtractor

def profile_extraction():
    extractor = KreuzbergTesseractExtractor()
    extractor.extract_text("test_documents/pdfs/fake-memo.pdf")

# Run profiler
cProfile.run('profile_extraction()', 'kreuzberg_profile.stats')

# Analyze results
stats = pstats.Stats('kreuzberg_profile.stats')
stats.sort_stats('cumulative')
stats.print_stats(20)
```

## Best Practices

1. **Always clear cache** before benchmarking for fair comparison
1. **Use appropriate timeouts** - OCR operations can be slow
1. **Test with representative data** - include various file types and sizes
1. **Monitor resource usage** - especially for large documents
1. **Compare multiple iterations** - account for system variability
1. **Document your configuration** - for reproducible results

## Conclusion

This guide provides comprehensive instructions for testing Kreuzberg's performance across different configurations, file types, and languages. The optimized Tesseract configuration consistently delivers the best performance, making it the recommended choice for production use.
