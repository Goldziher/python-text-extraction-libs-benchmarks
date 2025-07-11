# Benchmark Report

**Total Runs:** 4
**Total Files Processed:** 200
**Total Time:** 6.0 seconds

## Framework Performance Summary

| Framework       | Avg Success Rate | Avg Time (s) | Avg Memory (MB) | Files/sec |
| --------------- | ---------------- | ------------ | --------------- | --------- |
| kreuzberg_sync  | 90.0%            | 0.03         | 271.7           | 29.87     |
| kreuzberg_async | 90.0%            | 0.03         | 0.0             | 29.92     |

## Performance by Category

### Tiny

| Framework       | Success Rate | Avg Time (s) | Memory (MB) | Throughput |
| --------------- | ------------ | ------------ | ----------- | ---------- |
| kreuzberg_sync  | 90.0%        | 0.03         | 271.7       | 29.87      |
| kreuzberg_async | 90.0%        | 0.03         | 0.0         | 29.92      |

## Failure Analysis

| Error Type      | Count |
| --------------- | ----- |
| ValidationError | 20    |

## Performance Trends Over Iterations

**kreuzberg_sync:**

- Iteration 1: 0.07s
- Iteration 2: 0.00s

**kreuzberg_async:**

- Iteration 1: 0.07s
- Iteration 2: 0.00s

## Platform Comparison

### Darwin

| Framework       | Success Rate | Avg Time (s) |
| --------------- | ------------ | ------------ |
| kreuzberg_sync  | 90.0%        | 0.03         |
| kreuzberg_async | 90.0%        | 0.03         |
