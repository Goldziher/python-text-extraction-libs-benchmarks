# Test Documents

## Document Collection Overview

### Total Test Suite

- **94 files** across all categories
- **~210 MB** total size
- **Multiple languages** and formats
- **Real-world complexity** scenarios

## File Size Distribution

### Tiny Files (< 100 KB)

- **Count**: 15 files
- **Purpose**: Basic functionality testing
- **Formats**: TXT, JSON, CSV, small PDFs
- **Examples**: Simple text files, configuration files, small reports

### Small Files (100 KB - 1 MB)

- **Count**: 28 files
- **Purpose**: Typical document processing
- **Formats**: PDF, DOCX, XLSX, PPTX, HTML
- **Examples**: Letters, presentations, spreadsheets, web pages

### Medium Files (1 MB - 10 MB)

- **Count**: 32 files
- **Purpose**: Substantial document handling
- **Formats**: PDF reports, large presentations, image-heavy documents
- **Examples**: Technical manuals, marketing materials, academic papers

### Large Files (10 MB - 50 MB)

- **Count**: 15 files
- **Purpose**: Heavy document processing
- **Formats**: High-resolution PDFs, complex presentations
- **Examples**: Technical specifications, detailed reports, image collections

### Huge Files (> 50 MB)

- **Count**: 4 files
- **Purpose**: Stress testing and performance limits
- **Formats**: Very large PDFs, comprehensive documents
- **Examples**: Complete manuals, large datasets, multi-hundred page documents

## Format Coverage

### Document Formats

```yaml
PDF Documents:
  - Simple text PDFs
  - Image-heavy PDFs
  - Scanned documents
  - Form documents
  - Multi-language PDFs

Office Documents:
  - Microsoft Word (DOCX)
  - PowerPoint (PPTX)
  - Excel (XLSX)
  - LibreOffice formats

Web Formats:
  - HTML pages
  - XML documents
  - Markdown files
```

### Data Formats

```yaml
Structured Data:
  - JSON files
  - CSV datasets
  - XML data
  - YAML configurations

Text Formats:
  - Plain text (TXT)
  - Rich text (RTF)
  - Log files
  - Configuration files
```

### Image Formats

```yaml
Image Files:
  - PNG screenshots
  - JPEG photos
  - TIFF documents
  - BMP images
  - WEBP images

Image-containing Documents:
  - PDFs with embedded images
  - Presentations with graphics
  - Documents with charts/diagrams
```

## Language Distribution

### Primary Languages

- **English**: 65 files (69%)
- **German**: 8 files (8.5%)
- **Hebrew**: 6 files (6.4%)
- **Chinese**: 5 files (5.3%)
- **Japanese**: 4 files (4.3%)
- **Korean**: 3 files (3.2%)
- **Mixed/Other**: 3 files (3.2%)

### Language Detection Testing

Files are strategically named to test automatic language detection:

- `english_*` - English content
- `german_*` - German content
- `hebrew_*` - Hebrew content
- `chinese_*` - Chinese content
- `japanese_*` - Japanese content
- `korean_*` - Korean content

## Content Complexity

### Simple Documents

- Plain text
- Basic formatting
- Single language
- Standard fonts

### Moderate Complexity

- Mixed formatting
- Tables and lists
- Multiple sections
- Some images

### High Complexity

- Complex layouts
- Mixed languages
- Heavy graphics
- Forms and tables
- Technical diagrams

### Extreme Complexity

- Scanned documents
- Poor quality images
- Complex layouts
- Mixed content types
- Non-standard fonts

## Quality Assurance

### Document Validation

- All files manually verified
- Content quality assessed
- Format integrity confirmed
- Language accuracy checked

### Diversity Considerations

- Multiple domains represented
- Various complexity levels
- Different creation tools
- Real-world scenarios

### Privacy and Ethics

- No personal information
- No copyrighted content
- Publicly available sources
- Privacy-compliant collection

## Benchmark Scenarios

### Speed Testing

- Focus on typical document sizes
- Batch processing scenarios
- Single-file performance
- Throughput measurements

### Accuracy Testing

- Content preservation validation
- Format-specific extraction
- Metadata completeness
- Language detection accuracy

### Reliability Testing

- Error handling scenarios
- Timeout conditions
- Resource constraint testing
- Edge case handling

### Scalability Testing

- Large file processing
- Memory usage patterns
- Performance degradation
- Resource limit testing
