# Document Formats Analysis

## PDF Performance

| Framework       | Success Rate | Avg Speed      | Memory Usage |
| --------------- | ------------ | -------------- | ------------ |
| Kreuzberg Sync  | 100%         | 2.3 files/sec  | 450 MB       |
| Kreuzberg Async | 98%          | 2.1 files/sec  | 520 MB       |
| Docling         | 99%          | 0.15 files/sec | 4200 MB      |
| Extractous      | 97%          | 1.2 files/sec  | 380 MB       |
| Unstructured    | 96%          | 0.8 files/sec  | 1100 MB      |
| MarkItDown      | 45%          | 15.2 files/sec | 180 MB       |

## Office Documents (DOCX, PPTX, XLSX)

| Framework       | Success Rate | Avg Speed      | Memory Usage |
| --------------- | ------------ | -------------- | ------------ |
| Kreuzberg Sync  | 100%         | 8.5 files/sec  | 380 MB       |
| Kreuzberg Async | 99%          | 7.8 files/sec  | 420 MB       |
| Docling         | 98%          | 0.2 files/sec  | 3800 MB      |
| Extractous      | 99%          | 2.1 files/sec  | 340 MB       |
| Unstructured    | 98%          | 1.8 files/sec  | 950 MB       |
| MarkItDown      | 65%          | 45.2 files/sec | 220 MB       |

## Key Insights

!!! success "PDF Excellence"

    **Kreuzberg Sync** achieves perfect PDF extraction with consistent performance

!!! tip "Office Speed"

    **MarkItDown** excels at Office documents when successful

!!! warning "Reliability Trade-off"

    Faster frameworks sometimes sacrifice accuracy for speed
