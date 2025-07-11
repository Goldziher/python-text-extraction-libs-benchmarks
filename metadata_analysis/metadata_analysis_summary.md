# Metadata Richness Analysis Summary

## Overall Metadata Richness Rankings

### 1. Kreuzberg

**Score: 0.639 (63.9%)**

**Supported Fields:** 34
**Unique Capabilities:**

- Comprehensive 30+ field TypedDict metadata structure
- Type-safe metadata framework with IDE autocomplete
- Async-compatible metadata extraction
- Format-specific metadata extraction (PDF, Office, Images)
- Extensible metadata architecture with validation
- Clean separation of content and metadata
- Optional metadata enrichment via extras
- Multi-language metadata support
    **Limitations:**
- Requires optional extras for full metadata capabilities
- No pixel-perfect coordinate positioning
- Limited element-level categorization compared to Unstructured

### 2. Extractous

**Score: 0.264 (26.4%)**

**Supported Fields:** 10
**Unique Capabilities:**

- Comprehensive PDF metadata (permissions, encryption)
- Office document revisions and application info
- Standards-compliant Dublin Core fields
- Format-specific technical metadata
    **Limitations:**
- No spatial/coordinate information
- No document structure analysis
- No element-level metadata

### 3. Unstructured

**Score: 0.183 (18.3%)**

**Supported Fields:** 7
**Unique Capabilities:**

- Pixel-perfect coordinate positioning
- Element-level metadata
- Automatic content categorization
- Multi-language detection per element
- Layout reconstruction capability
    **Limitations:**
- No document property metadata (title, author)
- No content statistics (word count)
- No creation dates or document history

### 4. Docling

**Score: 0.099 (9.9%)**

**Supported Fields:** 4
**Unique Capabilities:**

- Advanced document structure modeling
- Separated content types (texts, tables, pictures)
- Binary document fingerprinting
- Schema-based document representation
    **Limitations:**
- No document property metadata
- No spatial coordinate information
- No content statistics

### 5. MarkItDown

**Score: 0.011 (1.1%)**

**Supported Fields:** 1
**Unique Capabilities:**

- LLM-optimized content structure
- Clean markdown output
- Lightweight processing
    **Limitations:**
- Minimal metadata extraction
- Focus on content conversion over metadata
- Requires optional dependencies for enhanced features

## Metadata Category Strengths

| Framework    | Document Properties | Content Statistics | Technical Properties | Spatial Layout | Document Structure |
| ------------ | ------------------- | ------------------ | -------------------- | -------------- | ------------------ |
| Extractous   | 30.3%               | 56.0%              | 36.0%                | 0.0%           | 0.0%               |
| Unstructured | 4.6%                | 0.0%               | 40.0%                | 91.0%          | 0.0%               |
| Docling      | 0.0%                | 16.3%              | 18.7%                | 0.0%           | 41.5%              |
| Kreuzberg    | 76.1%               | 51.3%              | 76.3%                | 32.7%          | 47.6%              |
| Markitdown   | 2.2%                | 0.0%               | 0.0%                 | 0.0%           | 0.0%               |
