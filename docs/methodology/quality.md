______________________________________________________________________

## title: Quality Assessment

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
1. **Heuristic Analysis**: Check for common extraction issues
1. **Format Validation**: Ensure output matches expected format
1. **Content Verification**: Validate extracted content makes sense

## Quality Grades

- **Excellent (90-100)**: Near-perfect extraction
- **Good (80-89)**: Minor issues, usable output
- **Fair (70-79)**: Some problems, mostly usable
- **Poor (60-69)**: Significant issues, limited use
- **Failed (\<60)**: Unusable extraction

## Framework Comparisons

Quality varies by:

- **File Format**: Some frameworks excel at specific formats
- **File Complexity**: Performance degrades with complexity
- **OCR Requirements**: Image-based text affects quality
- **Language**: Non-English text may impact scores
