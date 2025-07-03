# Comprehensive Benchmarking Design

## Overview

This document outlines the design for comprehensive, production-ready benchmarking of Python text extraction libraries with GitHub Actions CI/CD integration.

## Benchmarking Scenarios

### 1. Framework Configurations

- **Kreuzberg Sync**: Standard synchronous API
- **Kreuzberg Async**: Asynchronous API with concurrent processing
- **Docling**: Default configuration
- **MarkItDown**: Default configuration
- **Unstructured**: Default configuration with all document support

### 2. Document Categories to Test

#### Size-Based Categories

- **Tiny** (< 100KB): 20 documents
- **Small** (100KB - 1MB): 25 documents
- **Medium** (1MB - 10MB): 30 documents
- **Large** (10MB - 50MB): 15 documents
- **Huge** (> 50MB): 4 documents

#### Format-Based Categories

- **PDF Standard**: Regular PDFs with text
- **PDF Scanned**: OCR-required PDFs (rotated, scanned)
- **PDF Complex**: PDFs with tables, images, formulas
- **Office Documents**: DOCX, PPTX, XLSX, XLS, ODT
- **Web Documents**: HTML (various languages)
- **Text Documents**: Markdown, plain text, RST, Org
- **Email Documents**: MSG, EML
- **E-books**: EPUB
- **Data Formats**: CSV, JSON, YAML
- **Images**: PNG, JPEG, BMP (for OCR)

#### Language-Based Categories

- **English**: Standard ASCII text
- **Unicode**: Hebrew, German, Chinese, Japanese, Korean
- **Mixed**: Documents with multiple languages

### 3. Performance Scenarios

#### Throughput Tests

- **Sequential Processing**: One file at a time
- **Batch Processing**: Multiple files in sequence
- **Concurrent Processing** (async only): Multiple files in parallel
- **Memory Pressure**: Large files that stress memory limits
- **CPU Intensive**: Complex documents requiring heavy processing

#### Reliability Tests

- **Error Recovery**: Handling corrupted/malformed files
- **Timeout Handling**: Very large or complex files
- **Resource Limits**: Memory and CPU constraints
- **Mixed Workloads**: Various file types in sequence

### 4. Metrics to Collect

#### Primary Metrics

- **Extraction Time**: Total time from start to finish
- **Memory Usage**: Peak RSS, average RSS, memory growth
- **CPU Usage**: Average %, peak %, core utilization
- **Success Rate**: Successful vs failed extractions
- **Text Quality**: Character count, word count, structure preservation

#### Secondary Metrics

- **Startup Time**: Framework initialization overhead
- **Throughput**: Files/second, MB/second
- **Resource Efficiency**: Memory per MB processed
- **Error Details**: Failure reasons and patterns
- **Extraction Completeness**: Partial vs complete extraction

## Implementation Design

### 1. Enhanced Benchmark Runner

```python
class ComprehensiveBenchmarkRunner:
    """Enhanced benchmark runner with failure handling and multiple runs"""

    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.max_retries = 3
        self.cooldown_period = 5  # seconds between retries

    async def run_benchmark_suite(self):
        """Run complete benchmark suite with multiple iterations"""
        results = []

        for iteration in range(self.config.iterations):
            iteration_results = await self.run_single_iteration()
            results.extend(iteration_results)

            # Cooldown between iterations
            if iteration < self.config.iterations - 1:
                await asyncio.sleep(30)

        return results
```

### 2. Document Categorization

```python
@dataclass
class DocumentCategory:
    name: str
    size_range: tuple[int, int] | None
    file_types: list[FileType]
    languages: list[str]
    complexity: str  # simple, medium, complex

class DocumentCategorizer:
    """Categorize documents for organized testing"""

    def categorize_documents(self, test_dir: Path) -> dict[str, list[Path]]:
        categories = {
            'tiny': [],
            'small': [],
            'medium': [],
            'large': [],
            'huge': [],
            'pdf_standard': [],
            'pdf_scanned': [],
            'pdf_complex': [],
            'office': [],
            'web': [],
            'text': [],
            'email': [],
            'ebook': [],
            'data': [],
            'images': [],
            'english': [],
            'unicode': [],
            'mixed': []
        }
        # Implementation...
```

### 3. Failure Handling

```python
class ResilientExtractor:
    """Wrapper for extractors with retry logic and failure handling"""

    async def extract_with_retry(
        self,
        file_path: Path,
        max_retries: int = 3
    ) -> ExtractionResult:
        for attempt in range(max_retries):
            try:
                result = await self._attempt_extraction(file_path)
                return result
            except Exception as e:
                if attempt == max_retries - 1:
                    return ExtractionResult(
                        success=False,
                        error_type=type(e).__name__,
                        error_message=str(e),
                        partial_text=self._try_partial_extraction(file_path)
                    )
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### 4. Resource Monitoring

```python
class EnhancedResourceMonitor:
    """Advanced resource monitoring with detailed metrics"""

    def __init__(self):
        self.sampling_interval = 0.05  # 50ms for finer granularity
        self.metrics_buffer = []

    async def monitor(self):
        process = psutil.Process()

        while self.monitoring:
            metrics = {
                'timestamp': time.time(),
                'cpu_percent': process.cpu_percent(interval=None),
                'memory_rss': process.memory_info().rss,
                'memory_vms': process.memory_info().vms,
                'num_threads': process.num_threads(),
                'io_counters': process.io_counters()._asdict() if hasattr(process, 'io_counters') else None,
                'open_files': len(process.open_files()),
            }
            self.metrics_buffer.append(metrics)
            await asyncio.sleep(self.sampling_interval)
```

## GitHub Actions CI/CD Design

### 1. Workflow Structure

```yaml
name: Comprehensive Benchmarks

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:
    inputs:
      iterations:
        description: 'Number of benchmark iterations'
        required: false
        default: '3'

jobs:
  prepare:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.set-matrix.outputs.matrix }}
    steps:
      - name: Set up job matrix
        id: set-matrix
        run: |
          echo "matrix={\"framework\":[\"kreuzberg_sync\",\"kreuzberg_async\",\"docling\",\"markitdown\",\"unstructured\"],\"category\":[\"tiny\",\"small\",\"medium\",\"large\",\"pdf\",\"office\",\"web\"]}" >> $GITHUB_OUTPUT

  benchmark:
    needs: prepare
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        framework: ${{ fromJson(needs.prepare.outputs.matrix).framework }}
        category: ${{ fromJson(needs.prepare.outputs.matrix).category }}

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'

      - name: Install system dependencies
        run: |
          # OS-specific dependencies

      - name: Run benchmarks
        run: |
          uv run benchmark run \
            --framework ${{ matrix.framework }} \
            --category ${{ matrix.category }} \
            --iterations ${{ github.event.inputs.iterations || 3 }} \
            --output-dir results/${{ matrix.os }}/${{ matrix.framework }}/${{ matrix.category }}

      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: benchmark-results-${{ matrix.os }}-${{ matrix.framework }}-${{ matrix.category }}
          path: results/
          retention-days: 30

  aggregate:
    needs: benchmark
    runs-on: ubuntu-latest
    steps:
      - name: Download all artifacts
        uses: actions/download-artifact@v4

      - name: Aggregate results
        run: |
          uv run benchmark aggregate \
            --input-dir . \
            --output-dir aggregated-results

      - name: Generate report
        run: |
          uv run benchmark report \
            --results-dir aggregated-results \
            --output-format all

      - name: Upload final report
        uses: actions/upload-artifact@v4
        with:
          name: benchmark-report-${{ github.run_number }}
          path: aggregated-results/
          retention-days: 90
```

### 2. Performance Tracking

```yaml
  performance-regression:
    needs: aggregate
    runs-on: ubuntu-latest
    steps:
      - name: Download current results
        uses: actions/download-artifact@v4

      - name: Compare with baseline
        uses: benchmark-action/github-action-benchmark@v1
        with:
          tool: 'customBiggerIsBetter'
          output-file-path: aggregated-results/benchmark-summary.json
          github-token: ${{ secrets.GITHUB_TOKEN }}
          auto-push: true
          alert-threshold: '110%'
          comment-on-alert: true
          fail-on-alert: false
```

## Benchmark Configuration

### 1. Enhanced Configuration Structure

```python
@dataclass
class EnhancedBenchmarkConfig:
    # Execution settings
    iterations: int = 3
    warmup_runs: int = 1
    cooldown_seconds: int = 5

    # Resource limits
    timeout_seconds: int = 600  # 10 minutes per file
    max_memory_mb: int = 4096  # 4GB limit
    max_cpu_percent: int = 800  # 8 cores at 100%

    # Failure handling
    max_retries: int = 3
    retry_backoff: float = 2.0
    continue_on_error: bool = True

    # Categories to test
    categories: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)

    # Output settings
    save_intermediate: bool = True
    compression: bool = True
    detailed_errors: bool = True
```

### 2. Result Aggregation

```python
class ResultAggregator:
    """Aggregate results from multiple runs and machines"""

    def aggregate_results(self, result_dirs: list[Path]) -> AggregatedResults:
        all_results = []

        for result_dir in result_dirs:
            results = self.load_results(result_dir)
            all_results.extend(results)

        return AggregatedResults(
            raw_results=all_results,
            statistical_summary=self.calculate_statistics(all_results),
            performance_trends=self.analyze_trends(all_results),
            failure_analysis=self.analyze_failures(all_results),
            resource_utilization=self.analyze_resources(all_results)
        )
```

## Testing Strategy

### 1. Unit Tests for Components

- Extractor wrappers
- Resource monitoring
- Result aggregation
- Failure handling

### 2. Integration Tests

- End-to-end benchmark runs
- CI/CD pipeline validation
- Cross-platform compatibility

### 3. Performance Tests

- Benchmark overhead measurement
- Resource monitoring accuracy
- Scalability testing

## Expected Outcomes

### 1. Comprehensive Performance Data

- Detailed metrics for each framework/document combination
- Statistical analysis across multiple runs
- Platform-specific performance characteristics

### 2. Reliability Insights

- Failure patterns and recovery rates
- Resource consumption patterns
- Scalability limitations

### 3. Actionable Recommendations

- Framework selection guidance
- Performance optimization opportunities
- Resource allocation recommendations

## Next Steps

1. Implement enhanced benchmark runner with failure handling
1. Create document categorization system
1. Set up GitHub Actions workflows
1. Implement result aggregation and reporting
1. Create performance tracking dashboard
1. Document usage and interpretation guidelines
