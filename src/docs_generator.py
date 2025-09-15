from __future__ import annotations

import csv
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import msgspec

from src.types import (
    AggregatedResults,
    BenchmarkResult,
    ExtractionStatus,
    Framework,
)


class DocsGenerator:
    def __init__(self, docs_dir: Path = Path("docs")) -> None:
        self.docs_dir = docs_dir
        self.results_dir = docs_dir / "results"
        self.raw_data_dir = docs_dir / "raw-data"

    def _get_framework_name(self, framework: Any) -> str:
        return framework.value if hasattr(framework, "value") else str(framework)

    def generate_all(
        self,
        results_file: Path | None = None,
        aggregated_file: Path | None = None,
    ) -> None:
        results = self._load_results(results_file) if results_file else []
        aggregated = self._load_aggregated(aggregated_file) if aggregated_file else None

        self._setup_directories()

        self._generate_home_page(results, aggregated)
        self._generate_overview_page(results, aggregated)

        self._generate_file_type_pages(results)
        self._generate_file_size_pages(results)
        self._generate_framework_pages(results, aggregated)

        self._generate_csv_exports(results)

        self._generate_methodology_pages()

    def _setup_directories(self) -> None:
        dirs = [
            self.results_dir,
            self.results_dir / "by-file-type",
            self.results_dir / "by-file-size",
            self.results_dir / "by-framework",
            self.raw_data_dir,
            self.docs_dir / "methodology",
        ]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)

    def _load_results(self, results_file: Path) -> list[BenchmarkResult]:
        if not results_file.exists():
            return []
        try:
            with open(results_file, "rb") as f:
                data = msgspec.json.decode(f.read())
                if isinstance(data, list):
                    return [BenchmarkResult(**r) for r in data]
                if isinstance(data, dict) and "results" in data:
                    return [BenchmarkResult(**r) for r in data["results"]]
                return []
        except Exception:
            return []

    def _load_aggregated(self, aggregated_file: Path) -> AggregatedResults | None:
        if not aggregated_file or not aggregated_file.exists():
            return None
        with open(aggregated_file, "rb") as f:
            return msgspec.json.decode(f.read(), type=AggregatedResults)

    def _generate_home_page(
        self,
        results: list[BenchmarkResult],
        aggregated: AggregatedResults | None,
    ) -> None:
        by_file_type = self._aggregate_by_file_type(results)
        by_file_size = self._aggregate_by_file_size(results)
        by_framework = self._aggregate_by_framework(results)

        content = f"""---
title: Python Text Extraction Benchmarks 2025
description: Comprehensive performance analysis of Python text extraction frameworks
---

# Python Text Extraction Benchmarks 2025

## 🎯 Executive Summary

**Last Updated:** {datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")}

### Best Framework by Metric

| Metric | Winner | Score | Runner-up | Score |
|--------|--------|-------|-----------|-------|
{self._generate_winner_table(by_framework)}

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

| File Type | Files | Best Speed | Best Memory | Best Quality | Avg Time (s) |
|-----------|-------|------------|-------------|--------------|--------------|
{self._generate_file_type_summary_table(by_file_type)}

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
        scores = {{}}
        for framework, results in frameworks_results.items():
            success_rate = calc_success_rate(results) / 100  # normalize to 0-1
            throughput = calc_avg_speed(results)
            scores[framework] = success_rate * throughput  # combined score
        return max(scores.items(), key=lambda x: x[1])[0]  # framework with max score
    ```

| Size Category | Files | Avg Speed (f/s) | Avg Memory (MB) | Success Rate | Best Framework |
|---------------|-------|-----------------|-----------------|--------------|----------------|
{self._generate_file_size_summary_table(by_file_size)}

### Framework Comparison Matrix

!!! note "Grading System"
    **Grade Scale**: A+ (95-100), A (90-94), B+ (85-89), B (80-84), C+ (75-79), C (70-74), D (60-69), F (<60)

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

        return {{
            "speed_grade": score_to_grade(speed_score),
            "memory_grade": score_to_grade(memory_score),
            "quality_grade": score_to_grade(quality_score),
            "success_rate": success_rate,
            "overall_score": overall
        }}
    ```

| Framework | Formats | Speed Grade | Memory Grade | Quality Grade | Success % | Overall Score |
|-----------|---------|-------------|--------------|---------------|-----------|---------------|
{self._generate_framework_comparison_matrix(by_framework)}

## 📊 Quick Navigation

- [**Detailed Results Overview →**](results/overview.md)
- [**Results by File Type →**](results/by-file-type/index.md)
- [**Results by File Size →**](results/by-file-size/index.md)
- [**Results by Framework →**](results/by-framework/index.md)
- [**Download Raw Data (CSV) →**](raw-data/downloads.md)

## 🔍 Key Findings

{self._generate_key_findings(results, by_framework, by_file_type, by_file_size)}

## 📈 Methodology

Our benchmarks test {len({r.framework for r in results})} frameworks across {len({r.file_type for r in results})} file types with {len(results):,} total test runs.

- **Quality Assessment:** Enabled by default
- **Performance Profiling:** CPU and memory tracked at 50ms intervals
- **Timeout Protection:** 300 seconds per file
- **Test Categories:** All file sizes from <100KB to >50MB

[Learn more about our methodology →](methodology/benchmarking.md)
"""

        (self.docs_dir / "index.md").write_text(content)

    def _generate_overview_page(
        self,
        results: list[BenchmarkResult],
        aggregated: AggregatedResults | None,
    ) -> None:
        content = f"""---
title: Results Overview
description: Detailed benchmark results analysis
---

# Benchmark Results Overview

## Summary Statistics

- **Total Test Runs:** {len(results):,}
- **Successful Extractions:** {sum(1 for r in results if r.status == ExtractionStatus.SUCCESS):,}
- **Failed Extractions:** {sum(1 for r in results if r.status == ExtractionStatus.FAILED):,}
- **Timeouts:** {sum(1 for r in results if r.status == ExtractionStatus.TIMEOUT):,}
- **Average Extraction Time:** {sum(r.extraction_time for r in results) / len(results) if results else 0:.2f}s
- **Average Memory Usage:** {sum(r.peak_memory_mb for r in results) / len(results) if results else 0:.1f} MB

## Performance Distribution

{self._generate_performance_distribution(results)}

## Success Rate Analysis

{self._generate_success_rate_analysis(results)}

## Resource Usage Patterns

{self._generate_resource_patterns(results)}
"""

        (self.results_dir / "overview.md").write_text(content)

    def _generate_file_type_pages(self, results: list[BenchmarkResult]) -> None:
        by_file_type = self._aggregate_by_file_type(results)

        index_content = """---
title: Results by File Type
---

# Results by File Type

Select a file type to see detailed performance analysis:

"""
        for file_type, type_results in sorted(by_file_type.items()):
            count = len(type_results)
            avg_time = sum(r.extraction_time for r in type_results) / count
            index_content += f"- [**{file_type.upper()}** ({count} files, avg {avg_time:.2f}s)](/{file_type}.md)\n"

        (self.results_dir / "by-file-type" / "index.md").write_text(index_content)

        file_type_groups = {
            "pdf": ["pdf"],
            "docx": ["docx", "doc"],
            "spreadsheets": ["xlsx", "xls", "csv", "ods"],
            "images": ["png", "jpg", "jpeg", "bmp", "tiff", "gif", "webp"],
            "web": ["html", "xml", "mhtml"],
            "data": ["json", "csv", "tsv", "xml"],
        }

        for page_name, extensions in file_type_groups.items():
            page_results = []
            for ext in extensions:
                page_results.extend(by_file_type.get(ext.lower(), []))

            if page_results:
                self._generate_single_file_type_page(page_name, page_results)

    def _generate_single_file_type_page(
        self,
        file_type: str,
        results: list[BenchmarkResult],
    ) -> None:
        by_framework = defaultdict(list)
        for r in results:
            by_framework[r.framework].append(r)

        content = f"""---
title: {file_type.upper()} Extraction Performance
---

# {file_type.upper()} Extraction Performance

## Overview

- **Total Files Tested:** {len(results)}
- **Average Extraction Time:** {sum(r.extraction_time for r in results) / len(results) if results else 0:.2f}s
- **Average Memory Usage:** {sum(r.peak_memory_mb for r in results) / len(results) if results else 0:.1f} MB
- **Overall Success Rate:** {(sum(1 for r in results if r.status == ExtractionStatus.SUCCESS) / len(results) * 100) if results else 0:.1f}%

## Framework Comparison

| Framework | Files | Avg Time (s) | Avg Memory (MB) | Success Rate | Quality Score |
|-----------|-------|--------------|-----------------|--------------|---------------|
"""

        for framework in sorted(by_framework.keys(), key=lambda x: self._get_framework_name(x)):
            fw_results = by_framework[framework]
            if fw_results:
                avg_time = sum(r.extraction_time for r in fw_results) / len(fw_results)
                avg_mem = sum(r.peak_memory_mb for r in fw_results) / len(fw_results)
                success_rate = (
                    sum(1 for r in fw_results if r.status == ExtractionStatus.SUCCESS) / len(fw_results) * 100
                )
                quality = (sum(r.overall_quality_score or 0 for r in fw_results) / len(fw_results)) * 100

                framework_name = self._get_framework_name(framework)
                content += f"| {framework_name} | {len(fw_results)} | {avg_time:.2f} | {avg_mem:.1f} | {success_rate:.1f}% | {quality:.2f} |\n"

        content += f"""

## Performance by File Size

{self._generate_size_breakdown_for_type(results)}

## Quality Analysis

{self._generate_quality_analysis_for_type(results)}

## Sample Extraction Results

{self._generate_sample_extractions(results[:3])}
"""

        output_path = self.results_dir / "by-file-type" / f"{file_type}.md"
        output_path.write_text(content)

    def _generate_file_size_pages(self, results: list[BenchmarkResult]) -> None:
        by_size = self._aggregate_by_file_size(results)

        index_content = """---
title: Results by File Size
---

# Results by File Size

Performance analysis grouped by file size categories:

"""
        size_order = ["tiny", "small", "medium", "large", "huge"]
        for size_cat in size_order:
            if size_cat in by_size:
                size_results = by_size[size_cat]
                count = len(size_results)
                avg_time = sum(r.extraction_time for r in size_results) / count
                index_content += f"- [**{size_cat.title()}** ({count} files, avg {avg_time:.2f}s)]({size_cat}.md)\n"

        (self.results_dir / "by-file-size" / "index.md").write_text(index_content)

        for size_cat, size_results in by_size.items():
            self._generate_single_file_size_page(size_cat, size_results)

    def _generate_single_file_size_page(
        self,
        size_category: str,
        results: list[BenchmarkResult],
    ) -> None:
        size_ranges = {
            "tiny": "<100KB",
            "small": "100KB-1MB",
            "medium": "1MB-10MB",
            "large": "10MB-50MB",
            "huge": ">50MB",
        }

        by_framework = defaultdict(list)
        for r in results:
            by_framework[r.framework].append(r)

        content = f"""---
title: {size_category.title()} Files ({size_ranges.get(size_category, "Unknown")})
---

# {size_category.title()} Files Performance

## Size Range: {size_ranges.get(size_category, "Unknown")}

- **Total Files Tested:** {len(results)}
- **Average File Size:** {sum(r.file_size for r in results) / len(results) if results else 0 / 1024 / 1024:.2f} MB
- **Average Extraction Time:** {sum(r.extraction_time for r in results) / len(results) if results else 0:.2f}s
- **Average Memory Usage:** {sum(r.peak_memory_mb for r in results) / len(results) if results else 0:.1f} MB

## Framework Scalability

| Framework | Files | Avg Time (s) | Time/MB (s) | Memory/MB | Success Rate |
|-----------|-------|--------------|-------------|-----------|--------------|
"""

        for framework in sorted(by_framework.keys(), key=lambda x: self._get_framework_name(x)):
            fw_results = by_framework[framework]
            if fw_results:
                avg_time = sum(r.extraction_time for r in fw_results) / len(fw_results)
                avg_size_mb = sum(r.file_size for r in fw_results) / len(fw_results) / 1024 / 1024
                time_per_mb = avg_time / avg_size_mb if avg_size_mb > 0 else 0
                mem_per_mb = (
                    sum(r.peak_memory_mb for r in fw_results) / len(fw_results) / avg_size_mb if avg_size_mb > 0 else 0
                )
                success_rate = (
                    sum(1 for r in fw_results if r.status == ExtractionStatus.SUCCESS) / len(fw_results) * 100
                )

                framework_name = self._get_framework_name(framework)
                content += f"| {framework_name} | {len(fw_results)} | {avg_time:.2f} | {time_per_mb:.2f} | {mem_per_mb:.2f} | {success_rate:.1f}% |\n"

        content += f"""

## Performance Characteristics

{self._generate_size_performance_characteristics(results)}

## Resource Growth Analysis

{self._generate_resource_growth_analysis(results)}
"""

        output_path = self.results_dir / "by-file-size" / f"{size_category}.md"
        output_path.write_text(content)

    def _generate_framework_pages(
        self,
        results: list[BenchmarkResult],
        aggregated: AggregatedResults | None,
    ) -> None:
        by_framework = self._aggregate_by_framework(results)

        index_content = """---
title: Results by Framework
---

# Results by Framework

Detailed performance analysis for each framework:

"""
        for framework in sorted(by_framework.keys(), key=lambda x: self._get_framework_name(x)):
            fw_results = by_framework[framework]
            success_rate = sum(1 for r in fw_results if r.status == ExtractionStatus.SUCCESS) / len(fw_results) * 100
            framework_name = self._get_framework_name(framework)
            framework_filename = framework_name.lower().replace("_", "-")
            index_content += f"- [**{framework_name}** ({len(fw_results)} tests, {success_rate:.1f}% success)]({framework_filename}.md)\n"

        (self.results_dir / "by-framework" / "index.md").write_text(index_content)

        for framework, fw_results in by_framework.items():
            self._generate_single_framework_page(framework, fw_results)

    def _generate_single_framework_page(
        self,
        framework: Framework,
        results: list[BenchmarkResult],
    ) -> None:
        from src.config import get_supported_formats

        supported_formats = get_supported_formats(framework)

        content = f"""---
title: {self._get_framework_name(framework)} Performance Analysis
---

# {self._get_framework_name(framework)} Performance Analysis

## Framework Overview

- **Supported Formats:** {len(supported_formats)} ({", ".join(sorted(list(supported_formats)[:10]))}{", ..." if len(supported_formats) > 10 else ""})
- **Total Tests Run:** {len(results)}
- **Overall Success Rate:** {(sum(1 for r in results if r.status == ExtractionStatus.SUCCESS) / len(results) * 100) if results else 0:.1f}%
- **Average Extraction Time:** {sum(r.extraction_time for r in results) / len(results) if results else 0:.2f}s
- **Average Memory Usage:** {sum(r.peak_memory_mb for r in results) / len(results) if results else 0:.1f} MB

## Performance by File Type

{self._generate_framework_file_type_breakdown(results)}

## Performance by File Size

{self._generate_framework_file_size_breakdown(results)}

## Strengths and Weaknesses

{self._generate_framework_strengths_weaknesses(framework, results)}

## Error Analysis

{self._generate_framework_error_analysis(results)}
"""

        framework_name = self._get_framework_name(framework)
        output_path = self.results_dir / "by-framework" / f"{framework_name.lower().replace('_', '-')}.md"
        output_path.write_text(content)

    def _generate_csv_exports(self, results: list[BenchmarkResult]) -> None:
        full_csv_path = self.raw_data_dir / "full-results.csv"
        with open(full_csv_path, "w", newline="") as f:
            if results:
                fieldnames = [
                    "framework",
                    "file_path",
                    "file_type",
                    "file_size",
                    "category",
                    "status",
                    "extraction_time",
                    "peak_memory_mb",
                    "avg_memory_mb",
                    "peak_cpu_percent",
                    "character_count",
                    "word_count",
                    "overall_quality_score",
                    "error_message",
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for r in results:
                    writer.writerow(
                        {
                            "framework": self._get_framework_name(r.framework),
                            "file_path": r.file_path,
                            "file_type": r.file_type,
                            "file_size": r.file_size,
                            "category": self._get_framework_name(r.category) if r.category else "",
                            "status": r.status,
                            "extraction_time": r.extraction_time,
                            "peak_memory_mb": r.peak_memory_mb,
                            "avg_memory_mb": r.avg_memory_mb,
                            "peak_cpu_percent": r.peak_cpu_percent,
                            "character_count": r.character_count or 0,
                            "word_count": r.word_count or 0,
                            "overall_quality_score": r.overall_quality_score or 0,
                            "error_message": r.error_message or "",
                        }
                    )

        by_type_csv_path = self.raw_data_dir / "by-file-type.csv"
        self._generate_summary_csv(results, by_type_csv_path, "file_type")

        by_size_csv_path = self.raw_data_dir / "by-file-size.csv"
        self._generate_summary_csv(results, by_size_csv_path, "file_size")

        downloads_content = """---
title: Download Raw Data
---

# Download Raw Data

## Available CSV Files

- [**Full Results**](full-results.csv) - Complete benchmark results with all metrics
- [**By File Type Summary**](by-file-type.csv) - Aggregated results by file type
- [**By File Size Summary**](by-file-size.csv) - Aggregated results by file size

## Data Dictionary

### Full Results CSV

| Column | Description |
|--------|-------------|
| framework | Framework name |
| file_path | Path to test file |
| file_type | File extension |
| file_size | File size in bytes |
| category | Size category |
| status | Extraction status (SUCCESS/FAILED/TIMEOUT) |
| extraction_time | Time in seconds |
| peak_memory_mb | Peak memory usage in MB |
| avg_memory_mb | Average memory usage in MB |
| peak_cpu_percent | Peak CPU usage percentage |
| character_count | Extracted text character count |
| word_count | Extracted text word count |
| overall_quality_score | Quality assessment score (0-100) |
| error_message | Error details if failed |

## Usage

These CSV files can be imported into Excel, Google Sheets, or any data analysis tool for further analysis.
"""

        (self.raw_data_dir / "downloads.md").write_text(downloads_content)

    def _generate_methodology_pages(self) -> None:
        benchmarking_content = """---
title: Benchmarking Process
---

# Benchmarking Process

## Overview

Our benchmarking process is designed to provide fair, comprehensive, and reproducible performance measurements across all text extraction frameworks.

## Test Execution

1. **Warm-up Phase**: Each framework undergoes a warm-up iteration to eliminate cold-start effects
2. **Multiple Iterations**: Tests are run multiple times to ensure statistical significance
3. **Isolation**: Each framework is tested in isolation to prevent interference
4. **Cache Clearing**: Framework caches are cleared between tests for fairness

## File Selection

- **All Formats**: Each framework tests against all its supported file formats
- **All Sizes**: Files from <100KB to >50MB are tested
- **Real-world Documents**: Test suite includes actual documents, not synthetic data

## Resource Monitoring

- **CPU Usage**: Tracked at 50ms intervals
- **Memory Usage**: RSS (Resident Set Size) monitored continuously
- **Timeout Protection**: 300-second timeout per file extraction
- **Error Handling**: Failures are recorded with detailed error messages

## Quality Assessment

Quality assessment is enabled by default, measuring:
- Text completeness
- Extraction accuracy
- Metadata preservation
- Format handling

## Reproducibility

All benchmarks are:
- Version controlled
- Environment documented
- Seed controlled for randomization
- CI/CD automated
"""

        (self.docs_dir / "methodology" / "benchmarking.md").write_text(benchmarking_content)

        metrics_content = """---
title: Metrics Explained
---

# Metrics Explained

## Performance Metrics

### Speed Metrics

- **Extraction Time**: Wall-clock time for complete extraction (seconds)
- **Files per Second**: Throughput measurement for batch processing
- **Time per MB**: Normalized extraction time by file size

### Memory Metrics

- **Peak Memory (RSS)**: Maximum resident set size during extraction
- **Average Memory**: Mean memory usage throughout extraction
- **Memory per MB**: Memory usage normalized by file size

### CPU Metrics

- **Peak CPU%**: Maximum CPU utilization during extraction
- **Average CPU%**: Mean CPU utilization throughout extraction

## Quality Metrics

### Text Quality

- **Character Count**: Total characters extracted
- **Word Count**: Total words extracted
- **Completeness Score**: Percentage of content successfully extracted

### Accuracy Metrics

- **Quality Score**: Overall quality assessment (0-100)
- **Format Preservation**: How well formatting is maintained
- **Metadata Extraction**: Success in extracting document metadata

## Reliability Metrics

### Success Metrics

- **Success Rate**: Percentage of successful extractions
- **Partial Success Rate**: Files with partial content extracted
- **Timeout Rate**: Percentage of files that exceeded time limit

### Error Metrics

- **Failure Rate**: Percentage of complete failures
- **Error Categories**: Classification of failure types
- **Recovery Rate**: Ability to extract partial content on error

## Composite Scores

### Overall Score

Calculated as weighted average:
- Speed: 30%
- Memory Efficiency: 20%
- Quality: 30%
- Reliability: 20%

### Grade Calculation

- **A+**: 95-100
- **A**: 90-94
- **B+**: 85-89
- **B**: 80-84
- **C+**: 75-79
- **C**: 70-74
- **D**: 60-69
- **F**: <60
"""

        (self.docs_dir / "methodology" / "metrics.md").write_text(metrics_content)

        quality_content = """---
title: Quality Assessment
---

# Quality Assessment

## Overview

Quality assessment evaluates the completeness and accuracy of extracted text, enabled by default in all benchmarks.

## Assessment Criteria

### Text Completeness

- **Full Text Extraction**: All visible text is extracted
- **Hidden Text**: Extraction of comments, annotations, metadata
- **Special Characters**: Proper handling of Unicode, symbols
- **Language Support**: Multi-language text extraction

### Structure Preservation

- **Paragraph Boundaries**: Maintaining text flow
- **List Formatting**: Preserving bullet points and numbering
- **Table Structure**: Extracting tabular data correctly
- **Header/Footer**: Identifying document sections

### Metadata Extraction

- **Document Properties**: Title, author, creation date
- **Format-Specific Metadata**: PDF info, EXIF data
- **Embedded Resources**: Images, attachments references

## Scoring Algorithm

Quality scores are calculated using:

1. **Reference Comparison**: When available, compare against known good extraction
2. **Heuristic Analysis**: Check for common extraction issues
3. **Format Validation**: Ensure output matches expected format
4. **Content Verification**: Validate extracted content makes sense

## Quality Grades

- **Excellent (90-100)**: Near-perfect extraction
- **Good (80-89)**: Minor issues, usable output
- **Fair (70-79)**: Some problems, mostly usable
- **Poor (60-69)**: Significant issues, limited use
- **Failed (<60)**: Unusable extraction

## Framework Comparisons

Quality varies by:
- **File Format**: Some frameworks excel at specific formats
- **File Complexity**: Performance degrades with complexity
- **OCR Requirements**: Image-based text affects quality
- **Language**: Non-English text may impact scores
"""

        (self.docs_dir / "methodology" / "quality.md").write_text(quality_content)

    def _aggregate_by_file_type(self, results: list[BenchmarkResult]) -> dict[str, list[BenchmarkResult]]:
        by_type = defaultdict(list)
        for r in results:
            ext = Path(r.file_path).suffix.lower().lstrip(".")
            by_type[ext].append(r)
        return dict(by_type)

    def _aggregate_by_file_size(self, results: list[BenchmarkResult]) -> dict[str, list[BenchmarkResult]]:
        by_size = defaultdict(list)
        for r in results:
            size_mb = r.file_size / 1024 / 1024
            if size_mb < 0.1:
                category = "tiny"
            elif size_mb < 1:
                category = "small"
            elif size_mb < 10:
                category = "medium"
            elif size_mb < 50:
                category = "large"
            else:
                category = "huge"
            by_size[category].append(r)
        return dict(by_size)

    def _aggregate_by_framework(self, results: list[BenchmarkResult]) -> dict[Framework, list[BenchmarkResult]]:
        by_framework = defaultdict(list)
        for r in results:
            by_framework[r.framework].append(r)
        return dict(by_framework)

    def _generate_winner_table(self, by_framework: dict[Framework, list[BenchmarkResult]]) -> str:
        metrics = {}

        for framework, results in by_framework.items():
            if results:
                metrics[framework] = {
                    "speed": len(results) / sum(r.extraction_time for r in results),
                    "memory": sum(r.peak_memory_mb for r in results) / len(results) if results else 0,
                    "quality": (sum(r.overall_quality_score or 0 for r in results) / len(results) * 100)
                    if results
                    else 0,
                    "success": (sum(1 for r in results if r.status == ExtractionStatus.SUCCESS) / len(results) * 100)
                    if results
                    else 0,
                }

        rows = []
        metric_names = {
            "speed": "Speed (files/sec)",
            "memory": "Memory Efficiency",
            "quality": "Quality Score",
            "success": "Success Rate",
        }

        for metric, name in metric_names.items():
            if metric == "memory":
                sorted_fw = sorted(metrics.items(), key=lambda x: x[1][metric])
            else:
                sorted_fw = sorted(metrics.items(), key=lambda x: x[1][metric], reverse=True)

            if len(sorted_fw) >= 2:
                winner = self._get_framework_name(sorted_fw[0][0])
                winner_score = sorted_fw[0][1][metric]
                runner = self._get_framework_name(sorted_fw[1][0])
                runner_score = sorted_fw[1][1][metric]

                if metric == "speed":
                    rows.append(f"| {name} | {winner} | {winner_score:.2f} | {runner} | {runner_score:.2f} |")
                elif metric == "memory":
                    rows.append(f"| {name} | {winner} | {winner_score:.1f} MB | {runner} | {runner_score:.1f} MB |")
                else:
                    rows.append(f"| {name} | {winner} | {winner_score:.1f}% | {runner} | {runner_score:.1f}% |")

        return "\n".join(rows)

    def _generate_file_type_summary_table(self, by_file_type: dict[str, list[BenchmarkResult]]) -> str:
        rows = []

        for file_type in sorted(by_file_type.keys()):
            results = by_file_type[file_type]
            if not results:
                continue

            by_fw = defaultdict(list)
            for r in results:
                by_fw[r.framework].append(r)

            best_speed_fw = min(by_fw.items(), key=lambda x: sum(r.extraction_time for r in x[1]) / len(x[1]))[0]
            best_speed = self._get_framework_name(best_speed_fw)
            best_memory_fw = min(by_fw.items(), key=lambda x: sum(r.peak_memory_mb for r in x[1]) / len(x[1]))[0]
            best_memory = self._get_framework_name(best_memory_fw)

            quality_scores = {
                fw: (sum(r.overall_quality_score or 0 for r in rs) / len(rs)) * 100
                for fw, rs in by_fw.items()
                if any(r.overall_quality_score for r in rs)
            }
            if quality_scores:
                best_quality_fw = max(quality_scores.items(), key=lambda x: x[1])[0]
                best_quality = self._get_framework_name(best_quality_fw)
            else:
                best_quality = "N/A"

            avg_time = sum(r.extraction_time for r in results) / len(results) if results else 0

            rows.append(
                f"| {file_type.upper()} | {len(results)} | {best_speed} | "
                f"{best_memory} | {best_quality} | {avg_time:.2f} |"
            )

        return "\n".join(rows)

    def _generate_file_size_summary_table(self, by_file_size: dict[str, list[BenchmarkResult]]) -> str:
        rows = []
        size_order = ["tiny", "small", "medium", "large", "huge"]

        for size_cat in size_order:
            if size_cat not in by_file_size:
                continue

            results = by_file_size[size_cat]
            avg_speed = len(results) / sum(r.extraction_time for r in results)
            avg_memory = sum(r.peak_memory_mb for r in results) / len(results) if results else 0
            success_rate = (
                (sum(1 for r in results if r.status == ExtractionStatus.SUCCESS) / len(results) * 100) if results else 0
            )

            by_fw = defaultdict(list)
            for r in results:
                by_fw[r.framework].append(r)

            fw_scores = {}
            for fw, fw_results in by_fw.items():
                fw_success = sum(1 for r in fw_results if r.status == ExtractionStatus.SUCCESS) / len(fw_results)
                fw_speed = len(fw_results) / sum(r.extraction_time for r in fw_results)
                fw_scores[fw] = fw_success * fw_speed

            if fw_scores:
                best_fw_obj = max(fw_scores.items(), key=lambda x: x[1])[0]
                best_fw = self._get_framework_name(best_fw_obj)
            else:
                best_fw = "N/A"

            rows.append(
                f"| {size_cat.title()} | {len(results)} | {avg_speed:.2f} | "
                f"{avg_memory:.1f} | {success_rate:.1f}% | {best_fw} |"
            )

        return "\n".join(rows)

    def _generate_framework_comparison_matrix(self, by_framework: dict[Framework, list[BenchmarkResult]]) -> str:
        from src.config import get_supported_formats

        rows = []

        for framework in sorted(by_framework.keys(), key=lambda x: self._get_framework_name(x)):
            results = by_framework[framework]
            if not results:
                continue

            formats = len(get_supported_formats(framework))

            speed = len(results) / sum(r.extraction_time for r in results)
            memory = sum(r.peak_memory_mb for r in results) / len(results) if results else 0
            quality = (sum(r.overall_quality_score or 0 for r in results) / len(results) * 100) if results else 0
            success = (
                (sum(1 for r in results if r.status == ExtractionStatus.SUCCESS) / len(results) * 100) if results else 0
            )

            speed_grade = self._score_to_grade(speed * 10)
            memory_grade = self._score_to_grade(100 - min(memory, 100))
            quality_grade = self._score_to_grade(quality)

            overall = (
                self._grade_to_score(speed_grade) * 0.3
                + self._grade_to_score(memory_grade) * 0.2
                + self._grade_to_score(quality_grade) * 0.3
                + (success / 100) * 0.2
            ) * 5

            framework_name = self._get_framework_name(framework)
            rows.append(
                f"| {framework_name} | {formats} | {speed_grade} | "
                f"{memory_grade} | {quality_grade} | {success:.1f}% | {overall:.1f} |"
            )

        return "\n".join(rows)

    def _score_to_grade(self, score: float) -> str:
        if score >= 95:
            return "A+"
        if score >= 90:
            return "A"
        if score >= 85:
            return "B+"
        if score >= 80:
            return "B"
        if score >= 75:
            return "C+"
        if score >= 70:
            return "C"
        if score >= 60:
            return "D"
        return "F"

    def _grade_to_score(self, grade: str) -> float:
        grades = {"A+": 1.0, "A": 0.93, "B+": 0.87, "B": 0.83, "C+": 0.77, "C": 0.73, "D": 0.65, "F": 0.5}
        return grades.get(grade, 0.5)

    def _generate_key_findings(
        self,
        results: list[BenchmarkResult],
        by_framework: dict[Framework, list[BenchmarkResult]],
        by_file_type: dict[str, list[BenchmarkResult]],
        by_file_size: dict[str, list[BenchmarkResult]],
    ) -> str:
        findings = []

        speeds = {fw: len(rs) / sum(r.extraction_time for r in rs) for fw, rs in by_framework.items() if rs}
        if speeds:
            fastest = max(speeds.items(), key=lambda x: x[1])
            fastest_name = self._get_framework_name(fastest[0])
            findings.append(f"- **Fastest Framework:** {fastest_name} ({fastest[1]:.2f} files/sec)")

        memory = {fw: sum(r.peak_memory_mb for r in rs) / len(rs) for fw, rs in by_framework.items() if rs}
        if memory:
            efficient = min(memory.items(), key=lambda x: x[1])
            efficient_name = self._get_framework_name(efficient[0])
            findings.append(f"- **Most Memory Efficient:** {efficient_name} ({efficient[1]:.1f} MB avg)")

        quality = {
            fw: (sum(r.overall_quality_score or 0 for r in rs) / len(rs)) * 100
            for fw, rs in by_framework.items()
            if rs and any(r.overall_quality_score for r in rs)
        }
        if quality:
            best_quality = max(quality.items(), key=lambda x: x[1])
            best_quality_name = self._get_framework_name(best_quality[0])
            findings.append(f"- **Best Quality:** {best_quality_name} ({best_quality[1]:.1f}% score)")

        if by_file_type:
            hardest_type = min(
                by_file_type.items(),
                key=lambda x: sum(1 for r in x[1] if r.status == ExtractionStatus.SUCCESS) / len(x[1]),
            )
            findings.append(
                f"- **Most Challenging Format:** {hardest_type[0].upper()} "
                f"({sum(1 for r in hardest_type[1] if r.status == ExtractionStatus.SUCCESS) / len(hardest_type[1]) * 100:.1f}% success)"
            )

        if "huge" in by_file_size and "tiny" in by_file_size:
            huge_time = sum(r.extraction_time for r in by_file_size["huge"]) / len(by_file_size["huge"])
            tiny_time = sum(r.extraction_time for r in by_file_size["tiny"]) / len(by_file_size["tiny"])
            findings.append(f"- **Scalability Factor:** {huge_time / tiny_time:.1f}x slower for huge vs tiny files")

        return "\n".join(findings)

    def _generate_performance_distribution(self, results: list[BenchmarkResult]) -> str:
        times = [r.extraction_time for r in results]
        times.sort()

        if not times:
            return "No data available"

        p50 = times[len(times) // 2]
        p90 = times[int(len(times) * 0.9)]
        p99 = times[int(len(times) * 0.99)]

        return f"""
| Percentile | Time (s) |
|------------|----------|
| 50th (Median) | {p50:.2f} |
| 90th | {p90:.2f} |
| 99th | {p99:.2f} |
| Min | {min(times):.2f} |
| Max | {max(times):.2f} |
"""

    def _generate_success_rate_analysis(self, results: list[BenchmarkResult]) -> str:
        by_status = defaultdict(int)
        for r in results:
            by_status[r.status] += 1

        total = len(results)

        rows = []
        for status, count in sorted(by_status.items()):
            percentage = count / total * 100
            rows.append(f"| {status} | {count} | {percentage:.1f}% |")

        return f"""
| Status | Count | Percentage |
|--------|-------|------------|
{"".join(rows)}
"""

    def _generate_resource_patterns(self, results: list[BenchmarkResult]) -> str:
        return f"""
### Memory Usage Patterns

- **Average Memory:** {sum(r.peak_memory_mb for r in results) / len(results) if results else 0:.1f} MB
- **Peak Memory:** {max(r.peak_memory_mb for r in results) if results else 0:.1f} MB
- **Minimum Memory:** {min(r.peak_memory_mb for r in results) if results else 0:.1f} MB

### CPU Usage Patterns

- **Average CPU:** {sum(r.peak_cpu_percent for r in results) / len(results) if results else 0:.1f}%
- **Peak CPU:** {max(r.peak_cpu_percent for r in results) if results else 0:.1f}%
"""

    def _generate_size_breakdown_for_type(self, results: list[BenchmarkResult]) -> str:
        by_size = self._aggregate_by_file_size(results)

        rows = []
        for size_cat in ["tiny", "small", "medium", "large", "huge"]:
            if size_cat in by_size:
                size_results = by_size[size_cat]
                avg_time = sum(r.extraction_time for r in size_results) / len(size_results)
                success_rate = (
                    sum(1 for r in size_results if r.status == ExtractionStatus.SUCCESS) / len(size_results) * 100
                )
                rows.append(f"| {size_cat.title()} | {len(size_results)} | {avg_time:.2f}s | {success_rate:.1f}% |")

        if rows:
            return f"""
| Size Category | Files | Avg Time | Success Rate |
|---------------|-------|----------|--------------|
{"".join(rows)}
"""
        return "No size breakdown available"

    def _generate_quality_analysis_for_type(self, results: list[BenchmarkResult]) -> str:
        quality_results = [r for r in results if r.overall_quality_score is not None]

        if not quality_results:
            return "Quality assessment data not available"

        avg_quality = (sum(r.overall_quality_score for r in quality_results) / len(quality_results)) * 100

        return f"""
- **Average Quality Score:** {avg_quality:.1f}%
- **Files with Quality Data:** {len(quality_results)} / {len(results)}
- **Highest Quality:** {max(r.overall_quality_score for r in quality_results) * 100:.1f}%
- **Lowest Quality:** {min(r.overall_quality_score for r in quality_results) * 100:.1f}%
"""

    def _generate_sample_extractions(self, results: list[BenchmarkResult]) -> str:
        samples = []

        for r in results[:3]:
            if r.extracted_text:
                preview = r.extracted_text[:200].replace("\n", " ")
                samples.append(f"""
### {Path(r.file_path).name} - {self._get_framework_name(r.framework)}

- **Status:** {r.status}
- **Time:** {r.extraction_time:.2f}s
- **Characters:** {r.character_count or 0:,}
- **Preview:** "{preview}..."
""")

        return "\n".join(samples) if samples else "No sample extractions available"

    def _generate_size_performance_characteristics(self, results: list[BenchmarkResult]) -> str:
        if not results:
            return "No data available"

        avg_size_mb = sum(r.file_size for r in results) / len(results) if results else 0 / 1024 / 1024
        throughput_mbps = avg_size_mb / (sum(r.extraction_time for r in results) / len(results) if results else 0)

        return f"""
- **Average Throughput:** {throughput_mbps:.2f} MB/s
- **Files Processed:** {len(results)}
- **Total Data Processed:** {sum(r.file_size for r in results) / 1024 / 1024:.1f} MB
"""

    def _generate_resource_growth_analysis(self, results: list[BenchmarkResult]) -> str:
        if not results:
            return "No data available"

        size_memory_pairs = [(r.file_size / 1024 / 1024, r.peak_memory_mb) for r in results]
        size_memory_pairs.sort()

        if len(size_memory_pairs) > 1:
            sizes = [p[0] for p in size_memory_pairs]
            memories = [p[1] for p in size_memory_pairs]

            avg_size = sum(sizes) / len(sizes)
            avg_memory = sum(memories) / len(memories)

            if sizes[-1] > sizes[0]:
                growth_rate = (memories[-1] - memories[0]) / (sizes[-1] - sizes[0])
                return f"""
- **Memory Growth Rate:** {growth_rate:.2f} MB per MB of file size
- **Base Memory Usage:** ~{memories[0]:.1f} MB
- **Peak Memory Usage:** {max(memories):.1f} MB
"""

        return "Insufficient data for growth analysis"

    def _generate_framework_file_type_breakdown(self, results: list[BenchmarkResult]) -> str:
        by_type = self._aggregate_by_file_type(results)

        rows = []
        for file_type in sorted(by_type.keys()):
            type_results = by_type[file_type]
            avg_time = sum(r.extraction_time for r in type_results) / len(type_results)
            success_rate = (
                sum(1 for r in type_results if r.status == ExtractionStatus.SUCCESS) / len(type_results) * 100
            )
            rows.append(f"| {file_type.upper()} | {len(type_results)} | {avg_time:.2f}s | {success_rate:.1f}% |")

        return f"""
| File Type | Files | Avg Time | Success Rate |
|-----------|-------|----------|--------------|
{"".join(rows)}
"""

    def _generate_framework_file_size_breakdown(self, results: list[BenchmarkResult]) -> str:
        by_size = self._aggregate_by_file_size(results)

        rows = []
        for size_cat in ["tiny", "small", "medium", "large", "huge"]:
            if size_cat in by_size:
                size_results = by_size[size_cat]
                avg_time = sum(r.extraction_time for r in size_results) / len(size_results)
                avg_memory = sum(r.peak_memory_mb for r in size_results) / len(size_results)
                rows.append(f"| {size_cat.title()} | {len(size_results)} | {avg_time:.2f}s | {avg_memory:.1f} MB |")

        return f"""
| Size Category | Files | Avg Time | Avg Memory |
|---------------|-------|----------|------------|
{"".join(rows)}
"""

    def _generate_framework_strengths_weaknesses(
        self,
        framework: Framework,
        results: list[BenchmarkResult],
    ) -> str:
        by_type = self._aggregate_by_file_type(results)

        type_performance = {}
        for file_type, type_results in by_type.items():
            if type_results:
                success_rate = sum(1 for r in type_results if r.status == ExtractionStatus.SUCCESS) / len(type_results)
                avg_time = sum(r.extraction_time for r in type_results) / len(type_results)
                type_performance[file_type] = success_rate / avg_time

        if type_performance:
            sorted_types = sorted(type_performance.items(), key=lambda x: x[1], reverse=True)

            strengths = sorted_types[:3]
            weaknesses = sorted_types[-3:] if len(sorted_types) > 3 else []

            content = "### Strengths\n\n"
            for file_type, _ in strengths:
                type_results = by_type[file_type]
                success_rate = (
                    sum(1 for r in type_results if r.status == ExtractionStatus.SUCCESS) / len(type_results) * 100
                )
                content += f"- **{file_type.upper()}**: {success_rate:.1f}% success rate\n"

            if weaknesses:
                content += "\n### Areas for Improvement\n\n"
                for file_type, _ in weaknesses:
                    type_results = by_type[file_type]
                    success_rate = (
                        sum(1 for r in type_results if r.status == ExtractionStatus.SUCCESS) / len(type_results) * 100
                    )
                    content += f"- **{file_type.upper()}**: {success_rate:.1f}% success rate\n"

            return content

        return "Performance analysis not available"

    def _generate_framework_error_analysis(self, results: list[BenchmarkResult]) -> str:
        errors = defaultdict(int)
        for r in results:
            if r.status != ExtractionStatus.SUCCESS:
                if r.error_message:
                    if "timeout" in r.error_message.lower():
                        errors["Timeout"] += 1
                    elif "memory" in r.error_message.lower():
                        errors["Memory Error"] += 1
                    elif "format" in r.error_message.lower() or "support" in r.error_message.lower():
                        errors["Format Not Supported"] += 1
                    else:
                        errors["Other"] += 1
                else:
                    errors[r.status] += 1

        if errors:
            rows = []
            for error_type, count in sorted(errors.items(), key=lambda x: x[1], reverse=True):
                percentage = count / len(results) if results else 0
                rows.append(f"| {error_type} | {count} | {percentage:.1f}% |")

            return f"""
| Error Type | Count | Percentage |
|------------|-------|------------|
{"".join(rows)}
"""

        return "No errors recorded"

    def _generate_summary_csv(
        self,
        results: list[BenchmarkResult],
        output_path: Path,
        group_by: str,
    ) -> None:
        groups = defaultdict(list)

        for r in results:
            if group_by == "file_type":
                key = r.file_type
            elif group_by == "file_size":
                size_mb = r.file_size / 1024 / 1024
                if size_mb < 0.1:
                    key = "tiny"
                elif size_mb < 1:
                    key = "small"
                elif size_mb < 10:
                    key = "medium"
                elif size_mb < 50:
                    key = "large"
                else:
                    key = "huge"
            else:
                key = str(getattr(r, group_by))

            groups[key].append(r)

        with open(output_path, "w", newline="") as f:
            fieldnames = [group_by, "framework", "count", "avg_time", "avg_memory", "success_rate", "avg_quality"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for group_key, group_results in sorted(groups.items()):
                by_framework = defaultdict(list)
                for r in group_results:
                    framework_key = self._get_framework_name(r.framework)
                    by_framework[framework_key].append(r)

                for framework, fw_results in sorted(by_framework.items()):
                    writer.writerow(
                        {
                            group_by: group_key,
                            "framework": framework,
                            "count": len(fw_results),
                            "avg_time": sum(r.extraction_time for r in fw_results) / len(fw_results),
                            "avg_memory": sum(r.peak_memory_mb for r in fw_results) / len(fw_results),
                            "success_rate": sum(1 for r in fw_results if r.status == ExtractionStatus.SUCCESS)
                            / len(fw_results)
                            * 100,
                            "avg_quality": (sum(r.overall_quality_score or 0 for r in fw_results) / len(fw_results))
                            * 100,
                        }
                    )


if __name__ == "__main__":
    generator = DocsGenerator()
    generator.generate_all(
        results_file=Path("results/results.json"),
        aggregated_file=Path("results/aggregated.json"),
    )
