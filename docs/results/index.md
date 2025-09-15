______________________________________________________________________

## title: Latest Benchmark Results description: Comprehensive performance analysis of text extraction frameworks

# Latest Benchmark Results

!!! info "Benchmark Overview"

    **Generated**: From real benchmark results (1,479 files tested)
    **Frameworks**: 6 frameworks across 5 size categories
    **Test Files**: 94 unique files, 1,479 total test runs
    **Overall Success Rate**: 82.3%

## 🏆 Performance Rankings

### By Effective Throughput (Files/Second × Success Rate)

| Rank | Framework           | Raw Speed | Success Rate | Effective Speed | Memory (MB) |
| ---- | ------------------- | --------- | ------------ | --------------- | ----------- |
| 1    | **kreuzberg_sync**  | 7.04      | 100.0%       | **7.04**        | 562         |
| 2    | **kreuzberg_async** | 6.30      | 98.9%        | **6.23**        | 640         |
| 3    | **unstructured**    | 1.21      | 97.8%        | **1.18**        | 1393        |
| 4    | **extractous**      | 1.45      | 98.8%        | **1.43**        | 463         |
| 5    | **markitdown**      | 26.56     | 47.3%        | **12.57**       | 253         |
| 6    | **docling**         | 0.17      | 98.5%        | **0.17**        | 4350        |

### By Memory Efficiency (Lower is Better)

| Rank | Framework           | Memory (MB) | Effective Speed | Success Rate |
| ---- | ------------------- | ----------- | --------------- | ------------ |
| 1    | **markitdown**      | 253         | 12.57           | 47.3%        |
| 2    | **extractous**      | 463         | 1.43            | 98.8%        |
| 3    | **kreuzberg_sync**  | 562         | 7.04            | 100.0%       |
| 4    | **kreuzberg_async** | 640         | 6.23            | 98.9%        |
| 5    | **unstructured**    | 1393        | 1.18            | 97.8%        |
| 6    | **docling**         | 4350        | 0.17            | 98.5%        |

### By Success Rate

| Rank | Framework           | Success Rate | Effective Speed | Memory (MB) |
| ---- | ------------------- | ------------ | --------------- | ----------- |
| 1    | **kreuzberg_sync**  | 100.0%       | 7.04            | 562         |
| 2    | **extractous**      | 98.8%        | 1.43            | 463         |
| 3    | **kreuzberg_async** | 98.9%        | 6.23            | 640         |
| 4    | **docling**         | 98.5%        | 0.17            | 4350        |
| 5    | **unstructured**    | 97.8%        | 1.18            | 1393        |
| 6    | **markitdown**      | 47.3%        | 12.57           | 253         |

## 📊 Performance Overview

![Performance Comparison](assets/charts/performance_comparison_large.png)

## 📈 Key Insights

!!! success "Speed Champion"

    **markitdown** leads in processing speed at 26.6 files/second

!!! tip "Memory Efficient"

    **markitdown** uses the least memory at 253MB average

!!! check "Most Reliable"

    **kreuzberg_sync** achieves 100.0% success rate

## 📋 Detailed Analysis

Explore specific aspects of the benchmark results:

- **[Speed Analysis](performance/speed.md)** - Detailed speed comparisons
- **[Memory Analysis](performance/memory.md)** - Resource usage patterns
- **[Format Support](formats/index.md)** - File format compatibility
- **[Interactive Dashboard](interactive/dashboard.md)** - Explore the data yourself

______________________________________________________________________

*Data updated: 2025-09-13 12:57 UTC*
