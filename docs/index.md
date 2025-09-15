______________________________________________________________________

## title: Python Text Extraction Benchmarks 2025 description: Comprehensive performance analysis of Python text extraction frameworks

# Python Text Extraction Benchmarks 2025

## 🎯 Executive Summary

**Last Updated:** 2025-09-14 18:29 UTC

### Best Framework by Metric

| Metric | Winner | Score | Runner-up | Score |
| ------ | ------ | ----- | --------- | ----- |

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

| File Type | Files | Best Speed   | Best Memory  | Best Quality | Avg Time (s) |
| --------- | ----- | ------------ | ------------ | ------------ | ------------ |
| BMP       | 3     | unstructured | unstructured | N/A          | 0.00         |
| CSV       | 3     | unstructured | unstructured | unstructured | 0.00         |
| DOCX      | 42    | unstructured | unstructured | unstructured | 0.01         |
| EML       | 3     | unstructured | unstructured | unstructured | 0.00         |
| EPUB      | 6     | unstructured | unstructured | N/A          | 0.00         |
| HTML      | 51    | unstructured | unstructured | unstructured | 0.07         |
| JSON      | 3     | unstructured | unstructured | unstructured | 0.00         |
| MD        | 21    | unstructured | unstructured | N/A          | 0.00         |
| MSG       | 6     | unstructured | unstructured | unstructured | 0.07         |
| PDF       | 89    | unstructured | unstructured | N/A          | 0.11         |
| PNG       | 6     | unstructured | unstructured | N/A          | 0.00         |
| PPTX      | 12    | unstructured | unstructured | unstructured | 0.02         |
| TXT       | 12    | unstructured | unstructured | unstructured | 0.05         |
| XLS       | 3     | unstructured | unstructured | unstructured | 0.01         |
| XLSX      | 6     | unstructured | unstructured | unstructured | 0.17         |
| YAML      | 3     | unstructured | unstructured | unstructured | 0.23         |

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
        successful = sum(1 for result in results if result.status == "SUCCESS")
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
| Tiny          | 142   | 10.78           | 515.1           | 0.0%         | unstructured   |
| Small         | 73    | 34.63           | 534.0           | 0.0%         | unstructured   |
| Medium        | 36    | 25.61           | 554.1           | 0.0%         | unstructured   |
| Large         | 9     | 371.18          | 558.8           | 0.0%         | unstructured   |
| Huge          | 9     | 348.86          | 557.1           | 0.0%         | unstructured   |

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
        success_rate = sum(1 for r in results if r.status == "SUCCESS") / len(results) if results else 0 * 100

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

| Framework    | Formats | Speed Grade | Memory Grade | Quality Grade | Success % | Overall Score |
| ------------ | ------- | ----------- | ------------ | ------------- | --------- | ------------- |
| unstructured | 30      | A+          | F            | F             | 0.0%      | 2.8           |

## 📊 Quick Navigation

- [**Detailed Results Overview →**](results/overview.md)
- [**Results by File Type →**](results/by-file-type/index.md)
- [**Results by File Size →**](results/by-file-size/index.md)
- [**Results by Framework →**](results/by-framework/index.md)
- [**Download Raw Data (CSV) →**](raw-data/downloads.md)

## 🔍 Key Findings

- **Fastest Framework:** unstructured (16.07 files/sec)
- **Most Memory Efficient:** unstructured (528.3 MB avg)
- **Best Quality:** unstructured (0.3% score)
- **Most Challenging Format:** JSON (0.0% success)
- **Scalability Factor:** 0.0x slower for huge vs tiny files

## 📈 Methodology

Our benchmarks test 1 frameworks across 17 file types with 269 total test runs.

- **Quality Assessment:** Enabled by default
- **Performance Profiling:** CPU and memory tracked at 50ms intervals
- **Timeout Protection:** 300 seconds per file
- **Test Categories:** All file sizes from \<100KB to >50MB

[Learn more about our methodology →](methodology/benchmarking.md)
