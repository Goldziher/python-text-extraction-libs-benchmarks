# Image Extraction Analysis

## OCR Performance by Framework

| Framework       | Success Rate | Avg Speed      | Memory Usage | OCR Engine        |
| --------------- | ------------ | -------------- | ------------ | ----------------- |
| Kreuzberg Sync  | 95%          | 1.8 files/sec  | 650 MB       | Tesseract/EasyOCR |
| Kreuzberg Async | 94%          | 1.6 files/sec  | 720 MB       | Tesseract/EasyOCR |
| Docling         | 92%          | 0.08 files/sec | 5200 MB      | ML Models         |
| Extractous      | 85%          | 0.9 files/sec  | 520 MB       | Tesseract         |
| Unstructured    | 88%          | 0.6 files/sec  | 1400 MB      | Tesseract         |
| MarkItDown      | 25%          | 8.5 files/sec  | 380 MB       | Limited OCR       |

## Image Format Support

### Supported Formats

- **PNG**: All frameworks ✅
- **JPEG**: All frameworks ✅
- **TIFF**: Kreuzberg, Docling, Unstructured ✅
- **BMP**: Kreuzberg, Extractous ✅
- **WEBP**: Kreuzberg, Docling ✅

### Language Support

- **English**: All OCR-enabled frameworks
- **German**: Kreuzberg, Docling, Unstructured
- **French**: Kreuzberg, Docling, Unstructured
- **Chinese**: Kreuzberg, Docling
- **Hebrew**: Kreuzberg, Docling
- **Japanese**: Kreuzberg, Docling
- **Korean**: Kreuzberg, Docling

## Key Insights

!!! success "OCR Leader"

    **Kreuzberg** provides the best balance of speed and accuracy for image text extraction

!!! tip "Multilingual"

    **Docling** and **Kreuzberg** offer extensive language support

!!! info "Speed vs Quality"

    Image extraction requires significant computational resources - expect slower processing
