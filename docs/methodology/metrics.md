# Metrics & Scoring

## Performance Metrics

### Speed Measurements
- **Files per Second**: Primary speed metric
- **MB per Second**: Throughput for large files
- **Extraction Time**: Wall-clock time per file
- **Startup Overhead**: Framework initialization cost

### Memory Usage
- **Peak RSS**: Maximum resident set size
- **Average RSS**: Mean memory during extraction
- **Memory Efficiency**: MB per file processed
- **Memory Growth**: Memory leaks detection

### CPU Utilization
- **Average CPU %**: Mean utilization during extraction
- **Peak CPU %**: Maximum utilization spike
- **CPU Efficiency**: Processing per CPU cycle
- **Multi-core Usage**: Thread utilization patterns

## Quality Metrics

### Success Rate
- **Overall Success**: Files processed without errors
- **Format-Specific**: Success rate by file type
- **Size-Category**: Success rate by file size
- **Language-Specific**: Success for different languages

### Content Quality
- **Text Accuracy**: Character-level precision
- **Structure Preservation**: Format retention
- **Metadata Extraction**: Completeness of metadata
- **Language Detection**: Accuracy of language identification

## Scoring System

### Composite Scores
Each framework receives scores in multiple dimensions:

#### Speed Score (0-100)
```
Speed Score = (Framework Speed / Fastest Speed) × 100
```

#### Efficiency Score (0-100)
```
Efficiency = (1 / Memory Usage) × Success Rate × 100
```

#### Reliability Score (0-100)
```
Reliability = Success Rate × Quality Factor × 100
```

### Weighted Overall Score
```
Overall Score = (Speed × 0.3) + (Efficiency × 0.3) + (Reliability × 0.4)
```

## Benchmark Categories

### File Size Categories
- **Tiny**: < 100 KB (quick tests)
- **Small**: 100 KB - 1 MB (typical documents)
- **Medium**: 1 MB - 10 MB (substantial files)
- **Large**: 10 MB - 50 MB (heavy documents)
- **Huge**: > 50 MB (stress tests)

### Format Tiers
- **Universal**: PDF, DOCX, TXT, HTML
- **Common**: PPTX, XLSX, JSON, XML, CSV
- **All**: All supported formats including images

## Statistical Analysis

### Confidence Intervals
- 95% confidence intervals for all metrics
- Bootstrapping for robust estimates
- Outlier detection and handling
- Variance analysis across iterations

### Comparative Analysis
- Pairwise framework comparisons
- Statistical significance testing
- Effect size calculations
- Performance regression analysis

## Quality Assessment

### Content Validation
When `--enable-quality-assessment` is used:

- **Text Similarity**: Compare extracted content
- **Structure Analysis**: Evaluate format preservation
- **Metadata Completeness**: Assess information extraction
- **Language Accuracy**: Verify language detection

### Error Classification
- **Timeout Errors**: Exceeded time limits
- **Memory Errors**: Out of memory conditions
- **Format Errors**: Unsupported file types
- **Content Errors**: Extraction failures

## Reporting Standards

### Transparency
- All raw data available
- Methodology fully documented
- Reproducible test conditions
- Open source benchmarking code

### Bias Mitigation
- No framework-specific optimizations
- Identical test conditions
- Fair timeout policies
- Objective metric calculations

### Update Frequency
- Weekly automated runs
- Version update notifications
- Performance trend tracking
- Historical comparison data