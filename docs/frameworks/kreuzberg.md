# Kreuzberg

Fast, modern Python text extraction library with comprehensive format support and multiple OCR backends.

## 📊 Benchmark Performance

!!! success "Top Performer"

    **Overall Winner** in our benchmark suite

    - **Speed**: 15.66 files/second (fastest)
    - **Memory**: 259.8 MB average (efficient)
    - **Success Rate**: 100%\* (on supported formats)
    - **Installation**: 71 MB (compact)

### Performance Highlights

- ⚡ **Fastest processing** across all file size categories
- 🧠 **Memory efficient** with predictable usage patterns
- ⚖️ **Dual APIs** supporting both sync and async workflows
- 🎯 **Perfect reliability** on supported document formats

## 🚀 Key Features

### Multi-Format Support

- **PDF**: pypdfium2-based extraction with table detection
- **Office**: DOCX, PPTX, XLSX with native parsing
- **Images**: Multiple OCR backends (Tesseract, EasyOCR, PaddleOCR)
- **Web**: HTML with advanced table extraction
- **Archives**: ZIP, 7Z with recursive processing

### OCR Capabilities

```python
from kreuzberg import extract_text

# Automatic OCR backend selection
text = await extract_text("scanned_document.pdf")

# Specific OCR backend
text = await extract_text(
    "image.png",
    ocr_config={"backend": "easyocr", "languages": ["en", "de"]}
)
```

### Async/Sync Flexibility

```python
# Async API (recommended)
import asyncio
from kreuzberg import extract_text

async def process_documents(paths):
    tasks = [extract_text(path) for path in paths]
    return await asyncio.gather(*tasks)

# Sync API
from kreuzberg.sync import extract_text

text = extract_text("document.pdf")
```

## 📦 Installation & Setup

### Basic Installation

```bash
pip install kreuzberg
```

### With OCR Support

=== "EasyOCR (Recommended)"

    ```bash
    pip install kreuzberg[easyocr]
    ```

    - Best accuracy/speed balance
    - 80+ language support
    - GPU acceleration available

=== "Tesseract"

    ```bash
    # Install Tesseract first
    brew install tesseract  # macOS
    apt-get install tesseract-ocr  # Ubuntu

    pip install kreuzberg[tesseract]
    ```

    - Mature, stable OCR engine
    - Extensive language pack support
    - Lower memory usage

=== "PaddleOCR"

    ```bash
    pip install kreuzberg[paddleocr]
    ```

    - State-of-the-art accuracy
    - Chinese language optimized
    - Higher resource requirements

### Complete Installation

```bash
pip install kreuzberg[all]
```

## 💡 Usage Examples

### Basic Text Extraction

```python
import asyncio
from kreuzberg import extract_text

async def main():
    # Simple extraction
    text = await extract_text("document.pdf")
    print(f"Extracted {len(text)} characters")

    # With metadata
    result = await extract_text("document.pdf", include_metadata=True)
    print(f"Pages: {result.metadata.page_count}")
    print(f"Author: {result.metadata.author}")

asyncio.run(main())
```

### Batch Processing

```python
from pathlib import Path
import asyncio
from kreuzberg import extract_text

async def process_directory(directory: Path):
    """Process all documents in a directory."""
    tasks = []
    for file_path in directory.glob("**/*"):
        if file_path.suffix.lower() in {'.pdf', '.docx', '.png', '.jpg'}:
            tasks.append(extract_text(file_path))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    successful = sum(1 for r in results if isinstance(r, str))
    print(f"Processed {len(tasks)} files, {successful} successful")

asyncio.run(process_directory(Path("documents/")))
```

### Advanced Configuration

```python
from kreuzberg import extract_text, ExtractionConfig

config = ExtractionConfig(
    ocr_config={
        "backend": "easyocr",
        "languages": ["en", "de"],
        "gpu": True
    },
    table_extraction=True,
    chunk_processing=True,
    timeout=300
)

text = await extract_text("complex_document.pdf", config=config)
```

### Document Classification

```python
from kreuzberg import classify_document

# Automatic classification
classification = await classify_document("mystery_file.bin")
print(f"Detected: {classification.file_type} ({classification.confidence:.2f})")

# Extract based on classification
if classification.confidence > 0.8:
    text = await extract_text("mystery_file.bin")
```

## 🏗️ Architecture

### Design Philosophy

- **Performance First**: Optimized for speed without sacrificing quality
- **Async Native**: Built for modern Python async/await patterns
- **Plugin Architecture**: Extensible OCR and extraction backends
- **Type Safe**: Full mypy compatibility with comprehensive type hints

### Technical Implementation

```python
# Simplified architecture overview
class ExtractionEngine:
    def __init__(self):
        self.extractors = {
            '.pdf': PDFExtractor(),
            '.docx': DocxExtractor(),
            '.png': OCRExtractor(),
        }

    async def extract(self, file_path: Path) -> str:
        extractor = self.get_extractor(file_path)
        return await extractor.extract_text(file_path)
```

### Performance Optimizations

- **Lazy Loading**: OCR models loaded on demand
- **Memory Management**: Automatic cleanup of large objects
- **Concurrent Processing**: Parallel extraction with async/await
- **Cache Integration**: Built-in result caching for repeated operations

## ⚡ Performance Analysis

### Speed Breakdown by Format

| Format | Time/File | Throughput     | Success Rate |
| ------ | --------- | -------------- | ------------ |
| PDF    | 0.12s     | 8.3 files/sec  | 100%         |
| DOCX   | 0.08s     | 12.5 files/sec | 100%         |
| Images | 0.45s     | 2.2 files/sec  | 100%         |
| HTML   | 0.03s     | 33.3 files/sec | 100%         |

### Memory Usage Patterns

- **Base Memory**: ~50MB (framework overhead)
- **PDF Processing**: +100-200MB (per document)
- **OCR Processing**: +200-500MB (model loading)
- **Peak Memory**: Predictable, scales with document complexity

### Scaling Characteristics

- **Linear Scaling**: Performance scales with CPU cores
- **Async Efficiency**: Single-threaded async outperforms multi-threading
- **Memory Bound**: Performance limited by available RAM for large documents

## ✅ Advantages

- **🚀 Fastest Performance**: Consistently leads in speed benchmarks
- **💾 Memory Efficient**: Predictable and low memory usage
- **🔄 Modern APIs**: Both sync and async interfaces
- **📦 Lightweight**: 71MB installation size
- **🛠️ Extensible**: Plugin architecture for custom extractors
- **🧪 Type Safe**: Comprehensive type hints and mypy compatibility
- **📚 Well Documented**: Extensive documentation and examples

## ⚠️ Limitations

- **📧 No Email Support**: EML/MSG formats not supported (by design)
- **📊 Limited Data Formats**: No CSV/JSON/YAML extraction
- **🎯 Format Focus**: Optimized for document/image extraction
- **🆕 Newer Library**: Smaller community compared to established alternatives

## 🔗 Links & Resources

- **Documentation**: [https://kreuzberg.dev](https://kreuzberg.dev)
- **GitHub**: [https://github.com/Goldziher/kreuzberg](https://github.com/Goldziher/kreuzberg)
- **PyPI**: [https://pypi.org/project/kreuzberg/](https://pypi.org/project/kreuzberg/)
- **Benchmarks**: [https://benchmarks.kreuzberg.dev](https://benchmarks.kreuzberg.dev)

______________________________________________________________________

!!! tip "When to Choose Kreuzberg"

    Choose Kreuzberg for high-performance document processing where speed and efficiency are critical. Ideal for production systems processing large volumes of PDFs, office documents, and images.
