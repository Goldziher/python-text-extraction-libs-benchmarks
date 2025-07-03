"""Quality assessment for extracted text using ML-based metrics."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import msgspec
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from textstat import flesch_reading_ease, gunning_fog

from src.types import BenchmarkResult, ExtractionStatus


class TextQualityAssessor:
    """Assess quality of extracted text using various ML-based metrics."""

    def __init__(self) -> None:
        """Initialize quality assessment tools."""
        # Load sentence transformer for semantic similarity
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # TF-IDF vectorizer for lexical similarity
        self.tfidf = TfidfVectorizer(
            stop_words='english',
            max_features=5000,
            ngram_range=(1, 2)
        )

    def assess_extraction_quality(
        self, 
        extracted_text: str, 
        reference_text: str | None = None,
        file_path: Path | None = None
    ) -> dict[str, Any]:
        """Assess quality of extracted text."""
        
        quality_metrics = {}
        
        # Basic text statistics
        quality_metrics.update(self._basic_text_stats(extracted_text))
        
        # Content quality metrics
        quality_metrics.update(self._content_quality_metrics(extracted_text))
        
        # Readability metrics
        quality_metrics.update(self._readability_metrics(extracted_text))
        
        # Structural quality
        quality_metrics.update(self._structural_quality(extracted_text))
        
        # If reference text is available, compute similarity metrics
        if reference_text:
            quality_metrics.update(
                self._similarity_metrics(extracted_text, reference_text)
            )
        
        # Document-specific quality checks
        if file_path:
            quality_metrics.update(
                self._document_specific_quality(extracted_text, file_path)
            )
        
        return quality_metrics

    def _basic_text_stats(self, text: str) -> dict[str, Any]:
        """Calculate basic text statistics."""
        if not text.strip():
            return {
                'char_count': 0,
                'word_count': 0,
                'sentence_count': 0,
                'paragraph_count': 0,
                'avg_word_length': 0,
                'avg_sentence_length': 0
            }
        
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        paragraphs = text.split('\n\n')
        
        return {
            'char_count': len(text),
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'paragraph_count': len([p for p in paragraphs if p.strip()]),
            'avg_word_length': np.mean([len(word) for word in words]) if words else 0,
            'avg_sentence_length': np.mean([len(s.split()) for s in sentences if s.strip()]) if sentences else 0
        }

    def _content_quality_metrics(self, text: str) -> dict[str, Any]:
        """Assess content quality using various heuristics."""
        if not text.strip():
            return {
                'extraction_completeness': 0.0,
                'text_coherence': 0.0,
                'noise_ratio': 1.0,
                'gibberish_ratio': 1.0
            }
        
        # Estimate extraction completeness (heuristic based on content patterns)
        completeness = self._estimate_completeness(text)
        
        # Text coherence (based on sentence structure)
        coherence = self._estimate_coherence(text)
        
        # Noise ratio (special characters, repeated patterns)
        noise_ratio = self._calculate_noise_ratio(text)
        
        # Gibberish detection
        gibberish_ratio = self._detect_gibberish(text)
        
        return {
            'extraction_completeness': completeness,
            'text_coherence': coherence,
            'noise_ratio': noise_ratio,
            'gibberish_ratio': gibberish_ratio
        }

    def _readability_metrics(self, text: str) -> dict[str, Any]:
        """Calculate readability metrics."""
        if not text.strip():
            return {
                'flesch_reading_ease': 0,
                'gunning_fog_index': 100
            }
        
        try:
            flesch_score = flesch_reading_ease(text)
            gunning_fog_score = gunning_fog(text)
        except (ZeroDivisionError, ValueError):
            flesch_score = 0
            gunning_fog_score = 100
        
        return {
            'flesch_reading_ease': flesch_score,
            'gunning_fog_index': gunning_fog_score
        }

    def _structural_quality(self, text: str) -> dict[str, Any]:
        """Assess structural quality of extracted text."""
        if not text.strip():
            return {
                'has_proper_formatting': False,
                'maintains_line_breaks': False,
                'preserves_whitespace': False,
                'table_structure_preserved': False
            }
        
        # Check for proper formatting
        has_formatting = bool(re.search(r'[.!?]\s+[A-Z]', text))
        
        # Check line break preservation
        maintains_breaks = '\n' in text and len(text.split('\n')) > 3
        
        # Check whitespace preservation
        preserves_whitespace = '  ' in text or '\t' in text
        
        # Check table structure (basic heuristic)
        table_preserved = bool(re.search(r'\|.*\|', text) or 
                              re.search(r'\t.*\t', text) or
                              re.search(r'  +\w+  +\w+', text))
        
        return {
            'has_proper_formatting': has_formatting,
            'maintains_line_breaks': maintains_breaks,
            'preserves_whitespace': preserves_whitespace,
            'table_structure_preserved': table_preserved
        }

    def _similarity_metrics(self, extracted: str, reference: str) -> dict[str, Any]:
        """Calculate similarity metrics between extracted and reference text."""
        if not extracted.strip() or not reference.strip():
            return {
                'semantic_similarity': 0.0,
                'lexical_similarity': 0.0,
                'cosine_similarity': 0.0
            }
        
        # Semantic similarity using sentence transformers
        try:
            extracted_embedding = self.sentence_model.encode([extracted])
            reference_embedding = self.sentence_model.encode([reference])
            semantic_sim = cosine_similarity(extracted_embedding, reference_embedding)[0][0]
        except Exception:
            semantic_sim = 0.0
        
        # Lexical similarity using TF-IDF
        try:
            tfidf_matrix = self.tfidf.fit_transform([extracted, reference])
            lexical_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except Exception:
            lexical_sim = 0.0
        
        # Simple cosine similarity of word vectors
        try:
            extracted_words = set(extracted.lower().split())
            reference_words = set(reference.lower().split())
            intersection = len(extracted_words.intersection(reference_words))
            union = len(extracted_words.union(reference_words))
            jaccard_sim = intersection / union if union > 0 else 0
        except Exception:
            jaccard_sim = 0.0
        
        return {
            'semantic_similarity': float(semantic_sim),
            'lexical_similarity': float(lexical_sim),
            'jaccard_similarity': float(jaccard_sim)
        }

    def _document_specific_quality(self, text: str, file_path: Path) -> dict[str, Any]:
        """Assess quality based on document type."""
        file_type = file_path.suffix.lower()
        
        quality_checks = {
            'format_specific_score': 0.0,
            'expected_content_preserved': False
        }
        
        if file_type == '.pdf':
            # PDF-specific quality checks
            quality_checks.update(self._pdf_quality_checks(text))
        elif file_type in ['.docx', '.doc']:
            # Word document quality checks
            quality_checks.update(self._word_quality_checks(text))
        elif file_type == '.html':
            # HTML quality checks
            quality_checks.update(self._html_quality_checks(text))
        
        return quality_checks

    def _pdf_quality_checks(self, text: str) -> dict[str, Any]:
        """PDF-specific quality assessment."""
        # Check for common PDF extraction issues
        has_encoding_issues = bool(re.search(r'[^\x00-\x7F]+', text))
        has_ocr_artifacts = bool(re.search(r'\b[A-Z]{2,}\b.*\b[A-Z]{2,}\b', text))
        preserves_formatting = bool(re.search(r'\n\s*\n', text))
        
        score = 1.0
        if has_encoding_issues:
            score -= 0.3
        if has_ocr_artifacts:
            score -= 0.2
        if not preserves_formatting:
            score -= 0.2
            
        return {
            'format_specific_score': max(0.0, score),
            'has_encoding_issues': has_encoding_issues,
            'has_ocr_artifacts': has_ocr_artifacts,
            'preserves_pdf_formatting': preserves_formatting
        }

    def _word_quality_checks(self, text: str) -> dict[str, Any]:
        """Word document quality assessment."""
        # Check for proper text extraction from Word docs
        preserves_structure = bool(re.search(r'\n.*\n', text))
        has_metadata_pollution = bool(re.search(r'(Normal|Heading\d+|Header|Footer)', text))
        
        score = 1.0
        if has_metadata_pollution:
            score -= 0.3
        if not preserves_structure:
            score -= 0.2
            
        return {
            'format_specific_score': max(0.0, score),
            'preserves_word_structure': preserves_structure,
            'has_metadata_pollution': has_metadata_pollution
        }

    def _html_quality_checks(self, text: str) -> dict[str, Any]:
        """HTML quality assessment."""
        # Check for HTML tag remnants and proper text extraction
        has_html_tags = bool(re.search(r'<[^>]+>', text))
        has_script_content = bool(re.search(r'(function|var|document\.)', text))
        clean_extraction = not has_html_tags and not has_script_content
        
        score = 1.0 if clean_extraction else 0.5
        
        return {
            'format_specific_score': score,
            'clean_html_extraction': clean_extraction,
            'has_html_remnants': has_html_tags,
            'has_script_pollution': has_script_content
        }

    def _estimate_completeness(self, text: str) -> float:
        """Estimate extraction completeness using heuristics."""
        # Basic heuristic: check for common document patterns
        patterns = [
            r'\d+',  # Numbers
            r'[A-Z][a-z]+',  # Proper words
            r'[.!?]',  # Sentence endings
            r'\n',  # Line breaks
        ]
        
        score = 0.0
        for pattern in patterns:
            if re.search(pattern, text):
                score += 0.25
                
        return min(1.0, score)

    def _estimate_coherence(self, text: str) -> float:
        """Estimate text coherence."""
        sentences = re.split(r'[.!?]+', text)
        valid_sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        if not valid_sentences:
            return 0.0
        
        # Simple coherence check: ratio of valid sentences to total
        coherence = len(valid_sentences) / len(sentences) if sentences else 0
        return min(1.0, coherence)

    def _calculate_noise_ratio(self, text: str) -> float:
        """Calculate ratio of noise to content."""
        total_chars = len(text)
        if total_chars == 0:
            return 1.0
        
        # Count noise characters
        noise_chars = len(re.findall(r'[^\w\s.!?,-]', text))
        return min(1.0, noise_chars / total_chars)

    def _detect_gibberish(self, text: str) -> float:
        """Detect gibberish text using simple heuristics."""
        words = text.split()
        if not words:
            return 1.0
        
        # Check for patterns that indicate gibberish
        gibberish_patterns = 0
        for word in words:
            if len(word) > 15:  # Very long words
                gibberish_patterns += 1
            if re.search(r'[A-Z]{5,}', word):  # Too many capitals
                gibberish_patterns += 1
            if len(re.findall(r'[aeiou]', word.lower())) / len(word) < 0.1:  # No vowels
                gibberish_patterns += 1
        
        return min(1.0, gibberish_patterns / len(words))


def enhance_benchmark_results_with_quality(
    results_file: Path,
    reference_texts_dir: Path | None = None
) -> Path:
    """Enhance existing benchmark results with quality metrics."""
    
    # Load existing results
    with open(results_file, 'rb') as f:
        results_data = msgspec.json.decode(f.read())
    
    # Convert to BenchmarkResult objects if needed
    results = []
    for item in results_data:
        if isinstance(item, dict):
            results.append(BenchmarkResult(**item))
        else:
            results.append(item)
    
    # Initialize quality assessor
    assessor = TextQualityAssessor()
    
    # Enhance each result with quality metrics
    enhanced_results = []
    for result in results:
        enhanced_result = result
        
        # Only assess quality for successful extractions
        if result.status == ExtractionStatus.SUCCESS and result.extracted_text:
            
            # Look for reference text if directory provided
            reference_text = None
            if reference_texts_dir:
                ref_file = reference_texts_dir / f"{Path(result.file_path).stem}.txt"
                if ref_file.exists():
                    reference_text = ref_file.read_text(encoding='utf-8', errors='ignore')
            
            # Assess quality
            quality_metrics = assessor.assess_extraction_quality(
                result.extracted_text,
                reference_text,
                Path(result.file_path)
            )
            
            # Add quality metrics to result
            enhanced_result = msgspec.structs.replace(
                result,
                quality_metrics=quality_metrics,
                overall_quality_score=_calculate_overall_quality_score(quality_metrics)
            )
        
        enhanced_results.append(enhanced_result)
    
    # Save enhanced results
    output_file = results_file.parent / f"enhanced_{results_file.name}"
    with open(output_file, 'wb') as f:
        f.write(msgspec.json.encode(enhanced_results))
    
    return output_file


def _calculate_overall_quality_score(quality_metrics: dict[str, Any]) -> float:
    """Calculate overall quality score from individual metrics."""
    weights = {
        'extraction_completeness': 0.25,
        'text_coherence': 0.20,
        'semantic_similarity': 0.20,
        'format_specific_score': 0.15,
        'flesch_reading_ease': 0.10,
        'noise_ratio': -0.10  # Negative weight for noise
    }
    
    score = 0.0
    total_weight = 0.0
    
    for metric, weight in weights.items():
        if metric in quality_metrics:
            value = quality_metrics[metric]
            
            # Normalize some metrics
            if metric == 'flesch_reading_ease':
                value = min(100, max(0, value)) / 100
            elif metric == 'noise_ratio':
                value = 1 - value  # Invert so lower noise = higher score
            
            score += weight * value
            total_weight += abs(weight)
    
    return max(0.0, min(1.0, score / total_weight if total_weight > 0 else 0.0))