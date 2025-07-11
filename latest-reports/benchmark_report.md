# Benchmark Report

**Total Runs:** 18
**Total Files Processed:** 1548
**Total Time:** 6616.6 seconds

## Framework Performance Summary

| Framework       | Avg Success Rate | Avg Time (s) | Avg Memory (MB) | Files/sec |
| --------------- | ---------------- | ------------ | --------------- | --------- |
| kreuzberg_sync  | 82.0%            | 0.14         | 259.7           | 17.23     |
| kreuzberg_async | 82.0%            | 0.14         | 0.0             | 9.94      |
| docling         | 83.9%            | 9.07         | 1674.3          | 0.16      |
| markitdown      | 80.5%            | 9.73         | 382.4           | 9.87      |
| unstructured    | 90.0%            | 7.65         | 1544.9          | 2.26      |
| extractous      | 95.5%            | 5.27         | 406.8           | 2.52      |

## Performance by Category

### Tiny

| Framework       | Success Rate | Avg Time (s) | Memory (MB) | Throughput |
| --------------- | ------------ | ------------ | ----------- | ---------- |
| kreuzberg_sync  | 57.1%        | 0.03         | 243.8       | 35.31      |
| kreuzberg_async | 57.1%        | 0.08         | 0.0         | 12.99      |
| docling         | 71.4%        | 4.19         | 1573.3      | 0.24       |
| markitdown      | 69.4%        | 0.04         | 255.1       | 26.86      |
| unstructured    | 85.7%        | 0.17         | 1446.0      | 5.84       |
| extractous      | 93.9%        | 0.27         | 480.5       | 3.75       |

### Small

| Framework       | Success Rate | Avg Time (s) | Memory (MB) | Throughput |
| --------------- | ------------ | ------------ | ----------- | ---------- |
| kreuzberg_sync  | 88.9%        | 0.08         | 252.0       | 13.13      |
| kreuzberg_async | 88.9%        | 0.08         | 0.0         | 13.14      |
| docling         | 96.3%        | 13.95        | 1775.4      | 0.07       |
| markitdown      | 88.9%        | 0.37         | 272.8       | 2.71       |
| unstructured    | 92.6%        | 1.11         | 1546.7      | 0.90       |
| extractous      | 92.6%        | 0.27         | 371.3       | 3.75       |

### Medium

| Framework       | Success Rate | Avg Time (s) | Memory (MB) | Throughput |
| --------------- | ------------ | ------------ | ----------- | ---------- |
| kreuzberg_sync  | 100.0%       | 0.31         | 283.2       | 3.26       |
| kreuzberg_async | 100.0%       | 0.27         | 0.0         | 3.70       |
| markitdown      | 83.3%        | 28.80        | 619.4       | 0.03       |
| unstructured    | 91.7%        | 21.68        | 1642.0      | 0.05       |
| extractous      | 100.0%       | 15.29        | 368.6       | 0.07       |

## Failure Analysis

| Error Type                 | Count |
| -------------------------- | ----- |
| MissingDependencyError     | 114   |
| FileConversionException    | 45    |
| ConversionError            | 39    |
| ValidationError            | 30    |
| TypeError                  | 18    |
| OSError                    | 15    |
| UnsupportedFormatException | 9     |
| TesseractError             | 9     |
| UnicodeDecodeError         | 6     |

## Performance Trends Over Iterations

**docling:**

- Iteration 1: 7.76s
- Iteration 2: 8.36s
- Iteration 3: 8.93s

**extractous:**

- Iteration 1: 2.43s
- Iteration 2: 2.44s
- Iteration 3: 2.45s

**kreuzberg_async:**

- Iteration 1: 0.34s
- Iteration 2: 0.00s
- Iteration 3: 0.00s

**kreuzberg_sync:**

- Iteration 1: 0.30s
- Iteration 2: 0.00s
- Iteration 3: 0.00s

**markitdown:**

- Iteration 1: 2.14s
- Iteration 2: 5.57s
- Iteration 3: 5.45s

**unstructured:**

- Iteration 1: 3.47s
- Iteration 2: 3.50s
- Iteration 3: 3.54s

## Platform Comparison

### Linux

| Framework       | Success Rate | Avg Time (s) |
| --------------- | ------------ | ------------ |
| kreuzberg_sync  | 72.7%        | 0.10         |
| kreuzberg_async | 72.7%        | 0.11         |
| docling         | 80.3%        | 8.35         |
| markitdown      | 77.3%        | 4.38         |
| unstructured    | 88.6%        | 3.50         |
| extractous      | 94.3%        | 2.44         |
