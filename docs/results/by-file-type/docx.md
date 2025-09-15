______________________________________________________________________

## title: DOCX Extraction Performance

# DOCX Extraction Performance

## Overview

- **Total Files Tested:** 42
- **Average Extraction Time:** 0.01s
- **Average Memory Usage:** 516.9 MB
- **Overall Success Rate:** 0.0%

## Framework Comparison

| Framework    | Files | Avg Time (s) | Avg Memory (MB) | Success Rate | Quality Score |
| ------------ | ----- | ------------ | --------------- | ------------ | ------------- |
| unstructured | 42    | 0.01         | 516.9           | 0.0%         | 0.57          |

## Performance by File Size

| Size Category | Files | Avg Time | Success Rate |
| ------------- | ----- | -------- | ------------ |
| Tiny          | 39    | 0.01s    | 0.0%         |

## Quality Analysis

- **Average Quality Score:** 0.6%
- **Files with Quality Data:** 42 / 42
- **Highest Quality:** 0.7%
- **Lowest Quality:** 0.4%

## Sample Extraction Results

### word_tables.docx - unstructured

- **Status:** success
- **Time:** 0.09s
- **Characters:** 850
- **Preview:** "Test with tables A uniform table Header 0.0 Header 0.1 Header 0.2 Cell 1.0 Cell 1.1 Cell 1.2 Cell 2.0 Cell 2.1 Cell 2.2 A non-uniform table with horizontal spans Header 0.0 Header 0.1 Header 0.2 Cell ..."

### unit_test_lists.docx - unstructured

- **Status:** success
- **Time:** 0.01s
- **Characters:** 416
- **Preview:** "Test Document Paragraph 2.1.1 Paragraph 2.1.2 Test 1: List item 1 List item 2 List item 3 Test 2: List item a List item b List item c Test 3: List item 1 List item 2 List item 1.1 List item 1.2 List i..."

### fake.docx - unstructured

- **Status:** success
- **Time:** 0.01s
- **Characters:** 27
- **Preview:** "Lorem ipsum dolor sit amet...."
