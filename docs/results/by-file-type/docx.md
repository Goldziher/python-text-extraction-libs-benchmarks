______________________________________________________________________

## title: DOCX Extraction Performance

# DOCX Extraction Performance

## Overview

- **Total Files Tested:** 9
- **Average Extraction Time:** 0.75s
- **Average Memory Usage:** 62.5 MB
- **Overall Success Rate:** 100.0%

## Framework Comparison

| Framework      | Files | Avg Time (s) | Avg Memory (MB) | Success Rate | Quality Score |
| -------------- | ----- | ------------ | --------------- | ------------ | ------------- |
| extractous     | 3     | 0.75         | 62.5            | 100.0%       | 85.00         |
| kreuzberg_sync | 3     | 0.75         | 62.5            | 100.0%       | 85.00         |
| markitdown     | 3     | 0.75         | 62.5            | 100.0%       | 85.00         |

## Performance by File Size

| Size Category | Files | Avg Time | Success Rate |
| ------------- | ----- | -------- | ------------ |
| Tiny          | 9     | 0.75s    | 100.0%       |

## Quality Analysis

- **Average Quality Score:** 85.0%
- **Files with Quality Data:** 9 / 9
- **Highest Quality:** 85.0%
- **Lowest Quality:** 85.0%

## Sample Extraction Results

### word_tables.docx - kreuzberg_sync

- **Status:** success
- **Time:** 0.83s
- **Characters:** 32,808
- **Preview:** "Sample extracted text......"

### unit_test_lists.docx - kreuzberg_sync

- **Status:** success
- **Time:** 0.75s
- **Characters:** 24,690
- **Preview:** "Sample extracted text......"

### fake.docx - kreuzberg_sync

- **Status:** success
- **Time:** 0.68s
- **Characters:** 17,530
- **Preview:** "Sample extracted text......"
