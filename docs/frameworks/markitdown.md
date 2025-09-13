# MarkItDown

!!! info "Framework Overview"
    **Developer**: Microsoft
    **Language**: Python
    **Architecture**: Fast conversion to Markdown
    **Key Strength**: Blazing fast processing speed

## Overview

MarkItDown is Microsoft's lightweight document conversion framework focused on speed and Markdown output. It prioritizes fast processing over complex structure analysis, making it ideal for high-throughput scenarios.

## Key Features

### High-Speed Processing
- **Optimized for throughput**: 20-50+ files/second
- **Low memory footprint**: ~250MB average usage
- **Fast startup**: Minimal initialization overhead
- **Efficient batch processing**: Excellent for large document sets

### Format Support
- **Office documents**: DOCX, PPTX, XLSX
- **PDF documents**: Basic text extraction
- **Web formats**: HTML, XML
- **Data formats**: JSON, CSV, TXT
- **Image formats**: Limited OCR capability

### Markdown Focus
- **Clean Markdown output**: Well-formatted text
- **Structure preservation**: Headers, lists, tables
- **Link preservation**: URLs and references
- **Code block handling**: Technical documentation

## Performance Characteristics

### Strengths
- **Unmatched speed**: Fastest framework tested
- **Low resource usage**: Memory efficient
- **Simple integration**: Easy to use and deploy
- **Batch processing**: Excellent throughput

### Trade-offs
- **Limited accuracy**: ~47% overall success rate
- **Simple extraction**: Basic structure analysis
- **OCR limitations**: Minimal image text extraction
- **Complex documents**: Struggles with complex layouts

## Benchmark Results

### Speed Performance
- **Tiny files**: 180+ files/sec
- **Small files**: 45 files/sec
- **Medium files**: 26.6 files/sec
- **Large files**: 8.2 files/sec
- **Huge files**: 2.1 files/sec

### Success Rates
- **Overall**: 47.3%
- **Office documents**: 65%
- **Data formats**: 85%
- **PDF documents**: 25%
- **Images**: 15%

### Resource Usage
- **Average memory**: 253 MB
- **Peak memory**: 380 MB
- **CPU utilization**: 45% average
- **Disk I/O**: Low

## Use Cases

### Ideal For
- **High-volume processing**: Thousands of documents
- **Simple text extraction**: Basic content needs
- **Real-time applications**: Fast response requirements
- **Resource-constrained environments**: Limited memory/CPU
- **Markdown workflows**: Content publishing pipelines

### Consider Alternatives When
- **High accuracy needed**: Complex document structure
- **PDF-heavy workloads**: Scanned or complex PDFs
- **OCR requirements**: Image text extraction
- **Metadata extraction**: Comprehensive document info

## Configuration

### Installation
```bash
pip install markitdown>=0.1.3
```

### Basic Usage
```python
from markitdown import MarkItDown

converter = MarkItDown()
result = converter.convert("document.pdf")
markdown_text = result.text_content
```

### Advanced Configuration
```python
from markitdown import MarkItDown

converter = MarkItDown(
    # Enable available options
    use_file_extension_for_detection=True,
)

# Batch processing
for file_path in file_list:
    try:
        result = converter.convert(file_path)
        process_markdown(result.text_content)
    except Exception as e:
        handle_conversion_error(e)
```

## Integration Notes

### Framework Comparison
- **vs Docling**: 100x faster, much lower accuracy
- **vs Kreuzberg**: 3x faster, significantly lower accuracy
- **vs Unstructured**: 20x faster, lower success rate
- **vs Extractous**: 18x faster, lower reliability

### Production Considerations
- Implement quality checks for critical documents
- Use as first pass with fallback to accurate frameworks
- Monitor success rates by document type
- Consider hybrid approaches for different file types

## Recent Updates

### Version 0.1.3+
- Improved Office document support
- Better error handling
- Enhanced table extraction
- Optimized performance
- Additional format support

### Roadmap
- Improved PDF handling
- Better OCR integration
- Enhanced structure analysis
- Quality scoring system