______________________________________________________________________

## title: Metrics Explained

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
- **F**: \<60
