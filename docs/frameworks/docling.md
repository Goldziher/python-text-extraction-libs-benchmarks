# Docling

!!! info "Framework Overview"

    **Developer**: IBM Research
    **Language**: Python
    **Architecture**: ML-based document understanding
    **Key Strength**: Advanced PDF structure analysis

## Overview

Docling is IBM Research's state-of-the-art document processing framework that leverages machine learning models for intelligent document understanding. It excels at complex PDF analysis and structure extraction.

## Key Features

### Advanced PDF Processing

- **ML-based layout analysis**: Deep learning models for document structure
- **Table detection and extraction**: Sophisticated table understanding
- **Image and figure extraction**: Content-aware image handling
- **Multi-column layout support**: Complex document layouts

### Document Understanding

- **Semantic structure extraction**: Understanding document hierarchy
- **Content classification**: Automatic content type detection
- **Metadata enrichment**: Rich document metadata extraction
- **Language detection**: Automatic language identification

### Output Formats

- **Structured JSON**: Rich document representation
- **Markdown**: Clean text with structure
- **HTML**: Web-compatible output
- **Plain text**: Simple text extraction

## Performance Characteristics

### Strengths

- **Highest accuracy**: Best-in-class structure preservation
- **Complex documents**: Excels with challenging layouts
- **Rich metadata**: Comprehensive document information
- **Format support**: Strong PDF and Office document support

### Trade-offs

- **Processing speed**: Slower due to ML inference
- **Memory usage**: High memory requirements (4-5GB)
- **Startup time**: Model loading overhead
- **Resource intensive**: Requires significant computational resources

## Benchmark Results

### Speed Performance

- **Tiny files**: 0.8 files/sec
- **Small files**: 0.4 files/sec
- **Medium files**: 0.15 files/sec
- **Large files**: 0.08 files/sec
- **Huge files**: 0.03 files/sec

### Success Rates

- **Overall**: 98.5%
- **PDF documents**: 99.2%
- **Office documents**: 98.8%
- **Images**: 92.1%
- **Data formats**: 95.4%

### Resource Usage

- **Average memory**: 4.35 GB
- **Peak memory**: 6.2 GB
- **CPU utilization**: 85% average
- **Disk I/O**: Moderate

## Use Cases

### Ideal For

- **Enterprise document processing**: High-accuracy requirements
- **Complex PDF analysis**: Multi-column, complex layouts
- **Document digitization**: Converting scanned documents
- **Content management**: Rich metadata extraction
- **Research applications**: Academic paper processing

### Consider Alternatives When

- **High-speed processing needed**: Real-time applications
- **Resource constraints**: Limited memory environments
- **Simple documents**: Basic text extraction needs
- **Batch processing**: Large volume processing

## Configuration

### Installation

```bash
pip install docling>=2.52.0
```

### Basic Usage

```python
from docling import DocumentConverter

converter = DocumentConverter()
result = converter.convert("document.pdf")
text = result.document.export_to_markdown()
```

### Advanced Configuration

```python
from docling import DocumentConverter
from docling.datamodel.base_models import InputFormat

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=PipelineOptions(
                do_ocr=True,
                do_table_structure=True,
                table_structure_options=TableStructureOptions(
                    do_cell_matching=True
                )
            )
        )
    }
)
```

## Integration Notes

### Framework Comparison

- **vs Kreuzberg**: Similar accuracy, much slower
- **vs Unstructured**: Better structure analysis, higher resource usage
- **vs MarkItDown**: Much slower but higher accuracy
- **vs Extractous**: Better quality, significantly slower

### Production Considerations

- Monitor memory usage carefully
- Consider GPU acceleration for better performance
- Implement proper timeout handling
- Plan for longer processing times

## Recent Updates

### Version 2.52.0+

- Improved table detection accuracy
- Better multi-language support
- Enhanced image extraction
- Optimized memory usage
- Better error handling

### Roadmap

- GPU acceleration improvements
- Faster model inference
- Reduced memory footprint
- Additional format support
