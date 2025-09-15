# Unstructured

!!! info "Framework Overview"

    **Developer**: Unstructured Technologies
    **Language**: Python
    **Architecture**: Comprehensive document processing
    **Key Strength**: Broad format support and reliability

## Overview

Unstructured is a comprehensive document processing framework designed for production environments. It offers excellent format support, reliable processing, and enterprise-grade features.

## Key Features

### Extensive Format Support

- **60+ file types**: Most comprehensive format coverage
- **Document formats**: PDF, DOCX, PPTX, XLSX
- **Web formats**: HTML, XML, email formats
- **Data formats**: JSON, CSV, TSV
- **Image formats**: PNG, JPEG with OCR
- **Archive formats**: ZIP, TAR extraction

### Enterprise Features

- **Partitioning strategies**: Intelligent document segmentation
- **Element classification**: Content type identification
- **Metadata extraction**: Comprehensive document properties
- **Custom processors**: Extensible processing pipeline
- **API integrations**: Cloud and on-premise deployment

### Processing Pipeline

- **Document parsing**: Format-specific processors
- **Content extraction**: Text and structure analysis
- **Element detection**: Tables, images, headers
- **Chunking strategies**: Configurable segmentation
- **Output formatting**: Multiple export options

## Performance Characteristics

### Strengths

- **High reliability**: 97.8% overall success rate
- **Format breadth**: Handles almost any document type
- **Production ready**: Battle-tested in enterprise environments
- **Flexible output**: Multiple export formats
- **Good documentation**: Comprehensive guides and examples

### Trade-offs

- **Moderate speed**: 1.2 files/sec average
- **High memory usage**: 1.4GB average consumption
- **Complex setup**: Many configuration options
- **Installation size**: Large dependency footprint

## Benchmark Results

### Speed Performance

- **Tiny files**: 8.5 files/sec
- **Small files**: 2.8 files/sec
- **Medium files**: 1.21 files/sec
- **Large files**: 0.6 files/sec
- **Huge files**: 0.2 files/sec

### Success Rates

- **Overall**: 97.8%
- **PDF documents**: 97.5%
- **Office documents**: 98.2%
- **Images**: 88.3%
- **Data formats**: 99.1%

### Resource Usage

- **Average memory**: 1.39 GB
- **Peak memory**: 2.1 GB
- **CPU utilization**: 65% average
- **Disk I/O**: Moderate to high

## Use Cases

### Ideal For

- **Enterprise document processing**: Large-scale operations
- **Mixed format workflows**: Diverse document types
- **Content management systems**: Document ingestion
- **Data extraction pipelines**: Structured information retrieval
- **Production environments**: Reliable, scalable processing

### Consider Alternatives When

- **Speed is critical**: Real-time processing needs
- **Resource constraints**: Limited memory environments
- **Simple use cases**: Basic text extraction only
- **Cost sensitivity**: Resource usage optimization

## Configuration

### Installation

```bash
pip install unstructured[all-docs]>=0.18.14
```

### Basic Usage

```python
from unstructured.partition.auto import partition

elements = partition("document.pdf")
text = "\n".join([str(el) for el in elements])
```

### Advanced Configuration

```python
from unstructured.partition.auto import partition
from unstructured.staging.base import dict_to_elements

elements = partition(
    "document.pdf",
    strategy="hi_res",  # High resolution processing
    infer_table_structure=True,  # Extract table structure
    model_name="yolox",  # Object detection model
    include_page_breaks=True,  # Preserve page breaks
    languages=["en", "de", "fr"],  # Multi-language support
)

# Convert to structured format
element_dicts = [el.to_dict() for el in elements]
```

### Chunking Strategies

```python
from unstructured.chunking.title import chunk_by_title

chunks = chunk_by_title(
    elements,
    max_characters=1000,
    combine_text_under_n_chars=100,
    multipage_sections=True
)
```

## Integration Notes

### Framework Comparison

- **vs Kreuzberg**: Similar accuracy, slower processing
- **vs Docling**: Faster but less structure analysis
- **vs MarkItDown**: Much more accurate, significantly slower
- **vs Extractous**: More features, higher memory usage

### Production Considerations

- Configure appropriate chunking strategies
- Monitor memory usage in production
- Use hi_res strategy for critical documents
- Implement proper error handling and retries

## Recent Updates

### Version 0.18.14+

- Improved table extraction
- Better image processing
- Enhanced OCR capabilities
- Performance optimizations
- Additional format support

### Roadmap

- Faster processing speeds
- Reduced memory usage
- Better cloud integrations
- Enhanced ML models
- API improvements
