# Test Environment

## Hardware Specifications

### GitHub Actions Runners

- **CPU**: 2-core x86_64 (Intel/AMD)
- **Memory**: 7 GB RAM
- **Storage**: 14 GB SSD
- **OS**: Ubuntu 22.04 LTS
- **Python**: 3.13.7

### Performance Isolation

- Each framework runs in separate jobs
- Clean environment per test
- No shared state between frameworks
- Cache clearing before each run

## Software Environment

### Base Dependencies

```yaml
Python: 3.13.7
uv: latest (package manager)
System packages:
  - pandoc
  - tesseract-ocr (with language packs)
  - poppler-utils
  - libmagic1
```

### Language Support

```yaml
Tesseract Languages:
  - eng (English)
  - deu (German)
  - fra (French)
  - heb (Hebrew)
  - chi_sim (Chinese Simplified)
  - jpn (Japanese)
  - kor (Korean)
```

## Framework Isolation

### Dependency Management

Each framework runs with its specific dependencies:

- **Kreuzberg**: Latest version with OCR extras
- **Docling**: Latest with PyTorch backend
- **MarkItDown**: Latest with ONNX Runtime
- **Unstructured**: Latest with all-docs extras
- **Extractous**: Latest Rust-based version

### Resource Monitoring

- **CPU Usage**: Sampled every 50ms
- **Memory (RSS)**: Peak and average tracking
- **I/O Operations**: Read/write byte counts
- **Thread Count**: Active thread monitoring
- **File Handles**: Open file tracking

## Timeout Configuration

### Per-File Timeouts

- **Individual extraction**: 20 minutes (1200s)
- **Per-framework timeout**: 30 minutes total
- **Workflow timeout**: 6 hours per framework

### Error Handling

- Continue on individual file failures
- Save partial results on timeout
- Generate failure markers for aggregation
- Preserve successful extractions

## Reproducibility

### Consistent Conditions

- Same test documents for all frameworks
- Identical system configuration
- Fresh environment per run
- Deterministic processing order

### Version Control

- Framework versions locked in pyproject.toml
- Test documents versioned in repository
- Complete environment reproducible via uv

## Quality Assurance

### Data Validation

- Output format validation
- Content quality assessment
- Performance metric verification
- Cross-framework comparison

### Statistical Significance

- Multiple iterations per test (default: 3)
- Outlier detection and handling
- Confidence interval calculation
- Variance analysis across runs
