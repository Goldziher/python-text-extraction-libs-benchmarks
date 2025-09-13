# Extractous

!!! info "Framework Overview"
    **Developer**: Community/Rust-based
    **Language**: Rust with Python bindings
    **Architecture**: High-performance text extraction
    **Key Strength**: Speed and memory efficiency

## Overview

Extractous is a Rust-based text extraction framework with Python bindings, designed for high-performance document processing. It leverages Rust's performance and safety characteristics while providing a Python-friendly interface.

## Key Features

### Rust Performance
- **Native speed**: Compiled Rust backend
- **Memory safety**: Rust's ownership model prevents leaks
- **Multi-threading**: Efficient parallel processing
- **Zero-copy operations**: Minimal memory overhead
- **Cross-platform**: Consistent performance across systems

### Format Support
- **PDF documents**: Fast PDF text extraction
- **Office formats**: DOCX, XLSX, PPTX support
- **Web formats**: HTML, XML processing
- **Data formats**: JSON, CSV, plain text
- **Archive support**: ZIP, TAR file extraction

### Python Integration
- **Simple API**: Pythonic interface
- **Type hints**: Full typing support
- **Error handling**: Proper exception management
- **Async support**: Asynchronous processing options

## Performance Characteristics

### Strengths
- **Excellent speed**: 1.45 files/sec average
- **Memory efficient**: 463MB average usage
- **High reliability**: 98.8% success rate
- **Native performance**: Rust-compiled speed
- **Good balance**: Speed vs. accuracy trade-off

### Trade-offs
- **Limited advanced features**: Basic extraction focus
- **Smaller ecosystem**: Fewer extensions/plugins
- **OCR limitations**: Basic image text support
- **Installation complexity**: Rust toolchain dependencies

## Benchmark Results

### Speed Performance
- **Tiny files**: 12.5 files/sec
- **Small files**: 3.8 files/sec
- **Medium files**: 1.45 files/sec
- **Large files**: 0.8 files/sec
- **Huge files**: 0.3 files/sec

### Success Rates
- **Overall**: 98.8%
- **PDF documents**: 98.9%
- **Office documents**: 99.2%
- **Images**: 85.1%
- **Data formats**: 99.5%

### Resource Usage
- **Average memory**: 463 MB
- **Peak memory**: 680 MB
- **CPU utilization**: 55% average
- **Disk I/O**: Low to moderate

## Use Cases

### Ideal For
- **High-throughput processing**: Balanced speed and accuracy
- **Production systems**: Reliable document processing
- **Resource optimization**: Efficient memory usage
- **Batch processing**: Large document sets
- **Performance-critical applications**: Speed requirements

### Consider Alternatives When
- **Complex structure analysis needed**: Advanced layout understanding
- **Extensive OCR requirements**: Heavy image processing
- **Rich metadata extraction**: Comprehensive document info
- **Specialized format support**: Uncommon document types

## Configuration

### Installation
```bash
pip install extractous>=0.3.0
```

### Basic Usage
```python
from extractous import Extractor

extractor = Extractor()
text = extractor.extract_from_file("document.pdf")
```

### Advanced Configuration
```python
from extractous import Extractor, ExtractorConfig

config = ExtractorConfig(
    timeout=30,  # Extraction timeout in seconds
    max_memory=500_000_000,  # Max memory usage in bytes
    ocr_enabled=True,  # Enable OCR for images
    extract_metadata=True,  # Include document metadata
)

extractor = Extractor(config)

# Extract with metadata
result = extractor.extract_from_file_with_metadata("document.pdf")
text = result.text
metadata = result.metadata
```

### Batch Processing
```python
from extractous import Extractor
from pathlib import Path

extractor = Extractor()

def process_directory(directory_path):
    for file_path in Path(directory_path).rglob("*"):
        if file_path.is_file():
            try:
                text = extractor.extract_from_file(str(file_path))
                yield file_path.name, text
            except Exception as e:
                print(f"Failed to process {file_path}: {e}")
```

## Integration Notes

### Framework Comparison
- **vs Kreuzberg**: Similar accuracy, slightly faster
- **vs Docling**: Much faster, less structure analysis
- **vs MarkItDown**: Slower but much more reliable
- **vs Unstructured**: Faster, lower memory usage

### Production Considerations
- Monitor Rust runtime requirements
- Handle potential compilation dependencies
- Test cross-platform deployment
- Plan for Rust ecosystem updates

## Recent Updates

### Version 0.3.0+
- Improved PDF extraction accuracy
- Better error handling
- Enhanced metadata support
- Performance optimizations
- Additional format support

### Roadmap
- Advanced table extraction
- Better OCR integration
- Streaming processing support
- Enhanced metadata extraction
- Cloud deployment optimizations

## Technical Details

### Rust Backend
- Built with modern Rust (2021 edition)
- Uses proven parsing libraries
- Memory-safe operations
- Efficient multi-threading

### Python Bindings
- PyO3-based integration
- Native Python types
- Proper error propagation
- Type-safe interface