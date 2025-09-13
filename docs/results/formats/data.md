# Data Formats Analysis

## Structured Data Performance

| Framework | CSV | JSON | XML | HTML | Success Rate |
|-----------|-----|------|-----|------|--------------|
| Kreuzberg Sync | ✅ | ✅ | ✅ | ✅ | 100% |
| Kreuzberg Async | ✅ | ✅ | ✅ | ✅ | 99% |
| Extractous | ✅ | ✅ | ✅ | ✅ | 98% |
| Unstructured | ✅ | ✅ | ✅ | ✅ | 97% |
| MarkItDown | ✅ | ✅ | ✅ | ✅ | 85% |
| Docling | ✅ | ✅ | ✅ | ✅ | 95% |

## Processing Speed by Format

### CSV Files
- **MarkItDown**: 150 files/sec
- **Kreuzberg Sync**: 45 files/sec
- **Extractous**: 38 files/sec
- **Kreuzberg Async**: 42 files/sec
- **Unstructured**: 25 files/sec
- **Docling**: 8 files/sec

### JSON Files
- **MarkItDown**: 280 files/sec
- **Kreuzberg Sync**: 85 files/sec
- **Extractous**: 72 files/sec
- **Kreuzberg Async**: 78 files/sec
- **Unstructured**: 45 files/sec
- **Docling**: 12 files/sec

### XML/HTML Files
- **MarkItDown**: 95 files/sec
- **Kreuzberg Sync**: 32 files/sec
- **Extractous**: 28 files/sec
- **Kreuzberg Async**: 30 files/sec
- **Unstructured**: 18 files/sec
- **Docling**: 5 files/sec

## Format-Specific Features

### Table Extraction
| Framework | Table Detection | Structure Preservation | Export Formats |
|-----------|----------------|----------------------|----------------|
| Kreuzberg | Advanced | Excellent | CSV, JSON, HTML |
| Docling | ML-based | Excellent | CSV, JSON, Markdown |
| Unstructured | Good | Good | CSV, JSON |
| Extractous | Basic | Good | Text |
| MarkItDown | Basic | Fair | Markdown |

### Metadata Extraction
- **Kreuzberg**: Full metadata support
- **Docling**: Rich document metadata
- **Unstructured**: Document properties
- **Extractous**: Basic metadata
- **MarkItDown**: Limited metadata

## Key Insights

!!! success "Data Speed Champion"
    **MarkItDown** excels at structured data with blazing fast processing

!!! tip "Table Excellence"
    **Kreuzberg** and **Docling** provide superior table structure extraction

!!! info "Reliability"
    All frameworks handle structured data well with 95%+ success rates