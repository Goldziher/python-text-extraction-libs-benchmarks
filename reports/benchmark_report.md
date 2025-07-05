# Benchmark Report

**Total Runs:** 15
**Total Files Processed:** 1026
**Total Time:** 5573.8 seconds

## Framework Performance Summary

| Framework       | Avg Success Rate | Avg Time (s) | Avg Memory (MB) | Files/sec |
| --------------- | ---------------- | ------------ | --------------- | --------- |
| kreuzberg_sync  | 79.1%            | 0.11         | 0.0             | 35.75     |
| kreuzberg_async | 79.1%            | 0.11         | 0.0             | 24.46     |
| docling         | 82.8%            | 12.30        | 0.0             | 0.14      |
| markitdown      | 74.4%            | 14.23        | 0.0             | 10.62     |
| unstructured    | 88.6%            | 11.56        | 0.0             | 2.22      |

## Performance by Category

### Tiny

| Framework       | Success Rate | Avg Time (s) | Memory (MB) | Throughput |
| --------------- | ------------ | ------------ | ----------- | ---------- |
| kreuzberg_sync  | 57.4%        | 0.03         | 0.0         | 35.65      |
| kreuzberg_async | 57.4%        | 0.08         | 0.0         | 13.05      |
| docling         | 72.3%        | 4.27         | 0.0         | 0.23       |
| markitdown      | 68.1%        | 0.04         | 0.0         | 27.22      |
| unstructured    | 85.1%        | 0.17         | 0.0         | 5.74       |

### Small

| Framework       | Success Rate | Avg Time (s) | Memory (MB) | Throughput |
| --------------- | ------------ | ------------ | ----------- | ---------- |
| kreuzberg_sync  | 80.0%        | 0.01         | 0.0         | 68.21      |
| kreuzberg_async | 80.0%        | 0.02         | 0.0         | 55.98      |
| docling         | 93.3%        | 20.34        | 0.0         | 0.05       |
| markitdown      | 80.0%        | 0.22         | 0.0         | 4.62       |
| unstructured    | 93.3%        | 1.11         | 0.0         | 0.90       |

### Medium

| Framework       | Success Rate | Avg Time (s) | Memory (MB) | Throughput |
| --------------- | ------------ | ------------ | ----------- | ---------- |
| kreuzberg_sync  | 100.0%       | 0.30         | 0.0         | 3.38       |
| kreuzberg_async | 100.0%       | 0.23         | 0.0         | 4.35       |
| markitdown      | 75.0%        | 42.43        | 0.0         | 0.02       |
| unstructured    | 87.5%        | 33.39        | 0.0         | 0.03       |

## Failure Analysis

| Error Type                 | Count |
| -------------------------- | ----- |
| MissingDependencyError     | 114   |
| FileConversionException    | 45    |
| ConversionError            | 36    |
| ValidationError            | 24    |
| OSError                    | 15    |
| UnsupportedFormatException | 9     |
| UnicodeDecodeError         | 6     |
| TesseractError             | 6     |
| TypeError                  | 3     |

## Performance Trends Over Iterations

**docling:**

- Iteration 1: 8.33s
- Iteration 2: 8.95s
- Iteration 3: 9.59s

**kreuzberg_async:**

- Iteration 1: 0.26s
- Iteration 2: 0.00s
- Iteration 3: 0.00s

**kreuzberg_sync:**

- Iteration 1: 0.21s
- Iteration 2: 0.00s
- Iteration 3: 0.00s

**markitdown:**

- Iteration 1: 1.57s
- Iteration 2: 7.11s
- Iteration 3: 6.81s

**unstructured:**

- Iteration 1: 4.11s
- Iteration 2: 4.23s
- Iteration 3: 4.26s

## Platform Comparison

### Linux

| Framework       | Success Rate | Avg Time (s) |
| --------------- | ------------ | ------------ |
| kreuzberg_sync  | 67.1%        | 0.07         |
| kreuzberg_async | 67.1%        | 0.09         |
| docling         | 77.4%        | 8.96         |
| markitdown      | 71.4%        | 5.17         |
| unstructured    | 87.1%        | 4.20         |
