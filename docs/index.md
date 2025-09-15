______________________________________________________________________

## title: Python Text Extraction Benchmarks 2025 description: Comprehensive performance analysis of Python text extraction frameworks

# Python Text Extraction Benchmarks 2025

## 🎯 Executive Summary

**Last Updated:** 2025-09-15 09:53 UTC

### Best Framework by Metric

| Metric            | Winner         | Score   | Runner-up  | Score   |
| ----------------- | -------------- | ------- | ---------- | ------- |
| Speed (files/sec) | kreuzberg_sync | 1.33    | extractous | 1.33    |
| Memory Efficiency | kreuzberg_sync | 62.5 MB | extractous | 62.5 MB |
| Quality Score     | kreuzberg_sync | 85.0%   | extractous | 85.0%   |
| Success Rate      | kreuzberg_sync | 100.0%  | extractous | 100.0%  |

### Performance by File Type

!!! info "How we calculate these metrics"

    - **Best Speed**: Framework with lowest average extraction time for this file type
    - **Best Memory**: Framework with lowest peak memory usage (RSS) for this file type
    - **Best Quality**: Framework with highest average quality score (0-100 scale)
    - **Avg Time**: Mean extraction time across all frameworks

??? example "Python pseudocode for calculations"

    ```python
    # Best Speed calculation
    best_speed_fw = min(frameworks, key=lambda fw:
        sum(result.extraction_time for result in fw_results) / len(fw_results))

    # Best Memory calculation
    best_memory_fw = min(frameworks, key=lambda fw:
        sum(result.peak_memory_mb for result in fw_results) / len(fw_results))

    # Best Quality calculation
    best_quality_fw = max(frameworks, key=lambda fw:
        sum(result.quality_score or 0 for result in fw_results) / len(fw_results))

    # Average time across all frameworks
    avg_time = sum(all_extraction_times) / total_test_count
    ```

| File Type | Files | Best Speed     | Best Memory    | Best Quality   | Avg Time (s) |
| --------- | ----- | -------------- | -------------- | -------------- | ------------ |
| DOCX      | 9     | kreuzberg_sync | kreuzberg_sync | kreuzberg_sync | 0.75         |

### Performance by File Size

!!! tip "Calculation Details"

    - **Avg Speed**: Files per second throughput for this size category
    - **Avg Memory**: Average peak memory usage across all files in category
    - **Success Rate**: Percentage of successful extractions vs total attempts
    - **Best Framework**: Framework with best combined performance score

??? example "Python code for file size metrics"

    ```python
    # Average speed (throughput) calculation
    def calc_avg_speed(results):
        total_files = len(results)
        total_time = sum(result.extraction_time for result in results)
        return total_files / total_time  # files per second

    # Average memory calculation
    def calc_avg_memory(results):
        return sum(result.peak_memory_mb for result in results) / len(results) if results else 0

    # Success rate calculation
    def calc_success_rate(results):
        successful = sum(1 for result in results if result.status == ExtractionStatus.SUCCESS)
        return (successful / len(results) if results else 0) * 100

    # Best framework calculation
    def find_best_framework(frameworks_results):
        scores = {}
        for framework, results in frameworks_results.items():
            success_rate = calc_success_rate(results) / 100  # normalize to 0-1
            throughput = calc_avg_speed(results)
            scores[framework] = success_rate * throughput  # combined score
        return max(scores.items(), key=lambda x: x[1])[0]  # framework with max score
    ```

| Size Category | Files | Avg Speed (f/s) | Avg Memory (MB) | Success Rate | Best Framework |
| ------------- | ----- | --------------- | --------------- | ------------ | -------------- |
| Tiny          | 9     | 1.33            | 62.5            | 100.0%       | kreuzberg_sync |

### Framework Comparison Matrix

!!! note "Grading System"

    **Grade Scale**: A+ (95-100), A (90-94), B+ (85-89), B (80-84), C+ (75-79), C (70-74), D (60-69), F (\<60)

    **Overall Score** is weighted average: Speed 30% + Memory 20% + Quality 30% + Success 20%

??? example "Python code for grading system"

    ```python
    def score_to_grade(score):
        '''Convert 0-100 score to letter grade'''
        if score >= 95: return "A+"
        elif score >= 90: return "A"
        elif score >= 85: return "B+"
        elif score >= 80: return "B"
        elif score >= 75: return "C+"
        elif score >= 70: return "C"
        elif score >= 60: return "D"
        else: return "F"

    def calculate_overall_score(framework_results):
        # Speed: files per second (normalized to 0-100)
        speed = len(results) / sum(r.extraction_time for r in results)
        speed_score = min(speed * 10, 100)  # cap at 100

        # Memory: lower is better (inverted score)
        avg_memory = sum(r.peak_memory_mb for r in results) / len(results) if results else 0
        memory_score = max(0, 100 - min(avg_memory, 100))

        # Quality: direct average of quality scores
        quality_score = sum(r.quality_score or 0 for r in results) / len(results) if results else 0

        # Success rate: percentage successful
        success_rate = (sum(1 for r in results if r.status == ExtractionStatus.SUCCESS) / len(results) * 100) if results else 0

        # Weighted composite score (0-5 scale)
        overall = (
            speed_score * 0.3 +
            memory_score * 0.2 +
            quality_score * 0.3 +
            success_rate * 0.2
        ) / 100 * 5  # convert to 0-5 scale

        return {
            "speed_grade": score_to_grade(speed_score),
            "memory_grade": score_to_grade(memory_score),
            "quality_grade": score_to_grade(quality_score),
            "success_rate": success_rate,
            "overall_score": overall
        }
    ```

| Framework      | Formats | Speed Grade | Memory Grade | Quality Grade | Success % | Overall Score |
| -------------- | ------- | ----------- | ------------ | ------------- | --------- | ------------- |
| extractous     | 52      | F           | F            | B+            | 100.0%    | 3.6           |
| kreuzberg_sync | 25      | F           | F            | B+            | 100.0%    | 3.6           |
| markitdown     | 19      | F           | F            | B+            | 100.0%    | 3.6           |

## 📊 Quick Navigation

- [**Detailed Results Overview →**](results/overview.md)
- [**Results by File Type →**](results/by-file-type/index.md)
- [**Results by File Size →**](results/by-file-size/index.md)
- [**Results by Framework →**](results/by-framework/index.md)
- [**Download Raw Data (CSV) →**](raw-data/downloads.md)

## 🔍 Key Findings

- **Fastest Framework:** kreuzberg_sync (1.33 files/sec)
- **Most Memory Efficient:** kreuzberg_sync (62.5 MB avg)
- **Best Quality:** kreuzberg_sync (85.0% score)
- **Most Challenging Format:** DOCX (100.0% success)

## 📈 Methodology

Our benchmarks test 3 frameworks across 1 file types with 9 total test runs.

- **Quality Assessment:** Enabled by default
- **Performance Profiling:** CPU and memory tracked at 50ms intervals
- **Timeout Protection:** 300 seconds per file
- **Test Categories:** All file sizes from \<100KB to >50MB

[Learn more about our methodology →](methodology/benchmarking.md)
