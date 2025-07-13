# ~keep Architecture Overview

This document provides a systematic overview of the benchmark codebase organization and key components.

## Core Architecture

### 1. Benchmark Execution Pipeline

```
├── src/benchmark.py          # Main benchmark runner with multi-iteration support
├── src/extractors.py         # Framework wrapper implementations
├── src/profiler.py          # CPU/memory monitoring during extraction
├── src/categorizer.py       # Document size/type categorization
└── src/types.py             # Data structures and protocols
```

**Key Flow:**

1. `ComprehensiveBenchmarkRunner` orchestrates multi-iteration benchmarks
1. Handles both sync/async extractors uniformly with timeout protection
1. Profiles CPU/memory usage during extraction for resource analysis
1. Categorizes documents by size (tiny/small/medium/large/huge) for fair comparison
1. Aggregates results with failure analysis and quality metrics

### 2. Distributed CI Pipeline

```
├── .github/workflows/benchmark-by-framework.yml  # Main CI orchestration
├── .github/workflows/publish-reports.yml         # GitHub Pages deployment
└── results aggregation                           # Combine distributed results
```

**Strategy:**

- Each framework runs in isolated CI jobs to prevent interference
- Matrix strategy tests each framework across all document categories
- Results aggregated after all frameworks complete with graceful failure handling
- Artifacts stored for 90 days with automated GitHub Pages deployment

### 3. Data Processing & Analysis

```
├── src/aggregate.py         # Statistical aggregation from CI results
├── src/generate_index.py    # GitHub Pages HTML generation
├── src/reporting.py         # CSV exports and analysis reports
└── src/visualize.py         # Chart generation for comparisons
```

**Key Functions:**

- Groups results by framework/category for fair comparison
- Calculates speed (files/sec), memory (MB), success rates by category
- Prevents misleading averages (shows speed per category vs overall average)
- Creates framework comparison matrices and failure analysis

### 4. Quality Assurance

```
├── tests/test_calculations.py   # Verification of benchmark math
├── tests/test_aggregation.py    # Aggregation logic validation
└── tests/test_data/             # Real benchmark data fixtures
```

**Purpose:**

- Validates speed calculations (files/sec) against real benchmark data
- Ensures memory aggregation accuracy across categories
- Confirms success rate formulas are mathematically correct
- Protects against calculation errors that would mislead users

## Key Design Decisions

### Framework Isolation Strategy

- **Problem**: Shared memory, dependencies, or caching effects between frameworks
- **Solution**: Each framework runs in separate CI job with clean environment
- **Benefit**: Ensures fair comparison and eliminates interference

### Category-Based Metrics

- **Problem**: Misleading speed averages when frameworks test different file categories
- **Solution**: Display speed/memory by category rather than overall averages
- **Example**: If Framework A only tests tiny files, don't average with medium files

### Multi-Iteration Statistical Significance

- **Problem**: Single-run results can be misleading due to variance
- **Solution**: Multiple iterations with warmup/cooldown for statistical significance
- **Warmup**: Eliminates JIT compilation and framework initialization overhead
- **Cooldown**: Prevents thermal throttling and memory pressure between runs

### Graceful Failure Handling

- **Problem**: Framework failures should not block other frameworks or deployment
- **Solution**: Continue aggregation even with partial results, mark failures transparently
- **Benefit**: Provides useful partial results rather than complete failure

## File Organization

### Core Logic

- `benchmark.py` - Multi-iteration benchmark orchestration
- `extractors.py` - Framework wrapper implementations
- `aggregate.py` - Statistical result aggregation
- `generate_index.py` - Website generation from results

### Supporting Systems

- `profiler.py` - Resource monitoring (CPU/memory)
- `categorizer.py` - Document classification by size/type
- `config.py` - Framework configuration and exclusions
- `cli.py` - Command-line interface

### Analysis & Output

- `reporting.py` - CSV exports and console tables
- `visualize.py` - Chart generation (speed, memory, success rate)
- `html_report.py` - Detailed HTML analysis reports
- `interactive_dashboard.py` - Dynamic comparison interface

### Quality Assurance

- `tests/test_calculations.py` - Mathematical verification
- `tests/test_aggregation.py` - Logic validation
- `tests/test_data/` - Real benchmark data for testing

## Data Flow

1. **Benchmark Execution**: Multi-iteration runs with resource monitoring
1. **CI Distribution**: Framework isolation across parallel jobs
1. **Result Aggregation**: Statistical combination with failure analysis
1. **Website Generation**: Category-based tables and comparison charts
1. **Deployment**: Automated GitHub Pages with change detection
1. **Verification**: Test suite validates all calculations against real data

This architecture ensures fair framework comparison while providing reliable, transparent benchmark results.
