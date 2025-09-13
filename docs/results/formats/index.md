______________________________________________________________________

## title: File Format Analysis description: Performance analysis by file format

# File Format Support Analysis

## Format Coverage

Multiple file formats tested across all frameworks including PDF, DOCX, PPTX, images, and data formats.

## Category-Based Analysis

### Tiny Category

- **Files processed**: 747
- **Success rate**: 93.2%
- **Average speed**: 21.88 files/sec

### Small Category

- **Files processed**: 462
- **Success rate**: 92.2%
- **Average speed**: 3.04 files/sec

### Medium Category

- **Files processed**: 180
- **Success rate**: 85.0%
- **Average speed**: 0.69 files/sec

### Large Category

- **Files processed**: 45
- **Success rate**: 86.7%
- **Average speed**: 6.58 files/sec

### Huge Category

- **Files processed**: 45
- **Success rate**: 73.3%
- **Average speed**: 0.18 files/sec

## Format-Specific Insights

### Document Formats (.pdf, .docx, .pptx)

- **PDF**: Most challenging format, best handled by Docling and Kreuzberg
- **DOCX**: Generally well supported across frameworks
- **PPTX**: Good support with varying extraction quality

### Image Formats (.png, .jpg, .bmp)

- Requires OCR capabilities
- Kreuzberg and Unstructured show strong OCR performance
- Processing time varies significantly with image complexity

### Data Formats (.csv, .json, .yaml)

- Simple formats with high success rates
- Fast processing across most frameworks
- Format-specific parsing optimizations matter
