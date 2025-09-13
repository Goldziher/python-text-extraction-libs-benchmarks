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
        self.sentence_model = SentenceTransformer("all-MiniLM-L6-v2")

        self.tfidf = TfidfVectorizer(stop_words="english", max_features=5000, ngram_range=(1, 2))

    def assess_extraction_quality(
        self, extracted_text: str, reference_text: str | None = None, file_path: Path | None = None
    ) -> dict[str, Any]:
        """Assess quality of extracted text."""
        quality_metrics = {}

        quality_metrics.update(self._basic_text_stats(extracted_text))

        quality_metrics.update(self._content_quality_metrics(extracted_text))

        quality_metrics.update(self._readability_metrics(extracted_text))

        quality_metrics.update(self._structural_quality(extracted_text))

        if reference_text:
            quality_metrics.update(self._similarity_metrics(extracted_text, reference_text))

        if file_path:
            quality_metrics.update(self._document_specific_quality(extracted_text, file_path))

        return quality_metrics

    def _basic_text_stats(self, text: str) -> dict[str, Any]:
        """Calculate basic text statistics."""
        if not text.strip():
            return {
                "char_count": 0,
                "word_count": 0,
                "sentence_count": 0,
                "paragraph_count": 0,
                "avg_word_length": 0,
                "avg_sentence_length": 0,
            }

        words = text.split()
        sentences = re.split(r"[.!?]+", text)
        paragraphs = text.split("\n\n")

        return {
            "char_count": len(text),
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "paragraph_count": len([p for p in paragraphs if p.strip()]),
            "avg_word_length": float(np.mean([len(word) for word in words])) if words else 0.0,
            "avg_sentence_length": float(np.mean([len(s.split()) for s in sentences if s.strip()]))
            if sentences
            else 0.0,
        }

    def _content_quality_metrics(self, text: str) -> dict[str, Any]:
        """Assess content quality using various heuristics."""
        if not text.strip():
            return {"extraction_completeness": 0.0, "text_coherence": 0.0, "noise_ratio": 1.0, "gibberish_ratio": 1.0}

        completeness = self._estimate_completeness(text)

        coherence = self._estimate_coherence(text)

        noise_ratio = self._calculate_noise_ratio(text)

        gibberish_ratio = self._detect_gibberish(text)

        return {
            "extraction_completeness": completeness,
            "text_coherence": coherence,
            "noise_ratio": noise_ratio,
            "gibberish_ratio": gibberish_ratio,
        }

    def _readability_metrics(self, text: str) -> dict[str, Any]:
        """Calculate readability metrics."""
        if not text.strip():
            return {"flesch_reading_ease": 0, "gunning_fog_index": 100}

        try:
            flesch_score = flesch_reading_ease(text)
            gunning_fog_score = gunning_fog(text)
        except (ZeroDivisionError, ValueError):
            flesch_score = 0
            gunning_fog_score = 100

        return {"flesch_reading_ease": flesch_score, "gunning_fog_index": gunning_fog_score}

    def _structural_quality(self, text: str) -> dict[str, Any]:
        """Assess structural quality of extracted text."""
        if not text.strip():
            return {
                "has_proper_formatting": False,
                "maintains_line_breaks": False,
                "preserves_whitespace": False,
                "table_structure_preserved": False,
            }

        has_formatting = bool(re.search(r"[.!?]\s+[A-Z]", text))

        maintains_breaks = "\n" in text and len(text.split("\n")) > 3

        preserves_whitespace = "  " in text or "\t" in text

        table_preserved = bool(
            re.search(r"\|.*\|", text) or re.search(r"\t.*\t", text) or re.search(r"  +\w+  +\w+", text)
        )

        return {
            "has_proper_formatting": has_formatting,
            "maintains_line_breaks": maintains_breaks,
            "preserves_whitespace": preserves_whitespace,
            "table_structure_preserved": table_preserved,
        }

    def _similarity_metrics(self, extracted: str, reference: str) -> dict[str, Any]:
        """Calculate similarity metrics between extracted and reference text."""
        if not extracted.strip() or not reference.strip():
            return {"semantic_similarity": 0.0, "lexical_similarity": 0.0, "cosine_similarity": 0.0}

        try:
            extracted_embedding = self.sentence_model.encode([extracted])
            reference_embedding = self.sentence_model.encode([reference])
            semantic_sim = cosine_similarity(extracted_embedding, reference_embedding)[0][0]
        except Exception:
            semantic_sim = 0.0

        try:
            tfidf_matrix = self.tfidf.fit_transform([extracted, reference])
            lexical_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except Exception:
            lexical_sim = 0.0

        try:
            extracted_words = set(extracted.lower().split())
            reference_words = set(reference.lower().split())
            intersection = len(extracted_words.intersection(reference_words))
            union = len(extracted_words.union(reference_words))
            jaccard_sim = intersection / union if union > 0 else 0
        except Exception:
            jaccard_sim = 0.0

        return {
            "semantic_similarity": float(semantic_sim),
            "lexical_similarity": float(lexical_sim),
            "jaccard_similarity": float(jaccard_sim),
        }

    def _document_specific_quality(self, text: str, file_path: Path) -> dict[str, Any]:
        """Assess quality based on document type."""
        file_type = file_path.suffix.lower()

        quality_checks = {"format_specific_score": 0.0, "expected_content_preserved": False}

        if file_type == ".pdf":
            quality_checks.update(self._pdf_quality_checks(text))
        elif file_type in [".docx", ".doc"]:
            quality_checks.update(self._word_quality_checks(text))
        elif file_type == ".html":
            quality_checks.update(self._html_quality_checks(text))

        return quality_checks

    def _pdf_quality_checks(self, text: str) -> dict[str, Any]:
        """PDF-specific quality assessment."""
        has_encoding_issues = bool(
            re.search(r"[\ufffd]", text)
            or re.search(r"[ï¿½]+", text)
            or re.search(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]", text)
        )

        has_ocr_artifacts = bool(
            re.search(r"[|]{5,}", text)
            or re.search(r"[_]{5,}", text)
            or re.search(r"([^\w\s])\1{4,}", text)
            or re.search(r"\b\w{1,2}\s+\w{1,2}\s+\w{1,2}\s+\w{1,2}\b", text)
        )

        preserves_formatting = bool(re.search(r"\n\s*\n", text))

        score = 1.0
        if has_encoding_issues:
            score -= 0.3
        if has_ocr_artifacts:
            score -= 0.2
        if not preserves_formatting:
            score -= 0.2

        return {
            "format_specific_score": max(0.0, score),
            "has_encoding_issues": has_encoding_issues,
            "has_ocr_artifacts": has_ocr_artifacts,
            "preserves_pdf_formatting": preserves_formatting,
        }

    def _word_quality_checks(self, text: str) -> dict[str, Any]:
        """Word document quality assessment."""
        preserves_structure = bool(re.search(r"\n.*\n", text))
        has_metadata_pollution = bool(re.search(r"(Normal|Heading\d+|Header|Footer)", text))

        score = 1.0
        if has_metadata_pollution:
            score -= 0.3
        if not preserves_structure:
            score -= 0.2

        return {
            "format_specific_score": max(0.0, score),
            "preserves_word_structure": preserves_structure,
            "has_metadata_pollution": has_metadata_pollution,
        }

    def _html_quality_checks(self, text: str) -> dict[str, Any]:
        """HTML quality assessment."""
        has_html_tags = bool(re.search(r"<[^>]+>", text))
        has_script_content = bool(re.search(r"(function|var|document\.)", text))
        clean_extraction = not has_html_tags and not has_script_content

        score = 1.0 if clean_extraction else 0.5

        return {
            "format_specific_score": score,
            "clean_html_extraction": clean_extraction,
            "has_html_remnants": has_html_tags,
            "has_script_pollution": has_script_content,
        }

    def _estimate_completeness(self, text: str) -> float:
        """Estimate extraction completeness using heuristics."""
        patterns = [
            r"\d+",
            r"[A-Z][a-z]+",
            r"[.!?]",
            r"\n",
        ]

        score = 0.0
        for pattern in patterns:
            if re.search(pattern, text):
                score += 0.25

        return min(1.0, score)

    def _estimate_coherence(self, text: str) -> float:
        """Estimate text coherence."""
        sentences = re.split(r"[.!?]+", text)
        valid_sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        if not valid_sentences:
            return 0.0

        coherence = len(valid_sentences) / len(sentences) if sentences else 0
        return min(1.0, coherence)

    def _calculate_noise_ratio(self, text: str) -> float:
        """Calculate ratio of noise to content."""
        total_chars = len(text)
        if total_chars == 0:
            return 1.0

        noise_score = 0.0

        special_sequences = re.findall(r"[^\w\s]{3,}", text)
        if special_sequences:
            noise_score += min(0.3, len("".join(special_sequences)) / total_chars * 10)

        encoding_artifacts = len(re.findall(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]", text))
        if encoding_artifacts:
            noise_score += min(0.3, encoding_artifacts / total_chars * 50)

        excessive_spaces = len(re.findall(r"\s{5,}", text))
        if excessive_spaces:
            noise_score += min(0.2, excessive_spaces / 100)

        ocr_noise = len(re.findall(r"[|_]{3,}|([^\w\s])\1{2,}", text))
        if ocr_noise:
            noise_score += min(0.2, ocr_noise / 50)

        return min(1.0, noise_score)

    def _detect_gibberish(self, text: str) -> float:
        """Detect gibberish text using language-agnostic heuristics."""
        if not text.strip():
            return 1.0

        has_latin = bool(re.search(r"[a-zA-Z]", text))
        has_hebrew = bool(re.search(r"[\u0590-\u05FF]", text))
        has_chinese = bool(re.search(r"[\u4E00-\u9FFF]", text))
        has_japanese = bool(re.search(r"[\u3040-\u309F\u30A0-\u30FF]", text))
        has_korean = bool(re.search(r"[\uAC00-\uD7AF]", text))
        has_arabic = bool(re.search(r"[\u0600-\u06FF]", text))
        has_cyrillic = bool(re.search(r"[\u0400-\u04FF]", text))

        if has_hebrew or has_chinese or has_japanese or has_korean or has_arabic:
            special_char_ratio = len(re.findall(r"[^\w\s]", text)) / len(text)
            has_replacement_chars = "�" in text or "\ufffd" in text

            script_mixing_score = 0
            if has_hebrew and has_cyrillic:
                script_mixing_score = 0.8

            gibberish_score = 0.0
            if special_char_ratio > 0.3:
                gibberish_score += 0.3
            if has_replacement_chars:
                gibberish_score += 0.4
            gibberish_score += script_mixing_score

            return min(1.0, gibberish_score)

        words = re.findall(r"\b\w+\b", text)
        if not words:
            return 1.0

        gibberish_patterns = 0
        total_checks = 0

        for word in words[:200]:
            if len(word) > 2:
                total_checks += 1

                if len(word) > 20 and "-" not in word:
                    gibberish_patterns += 1

                elif has_latin and len(word) > 3:
                    vowel_ratio = len(re.findall(r"[aeiouAEIOU]", word)) / len(word)
                    if vowel_ratio < 0.1:
                        gibberish_patterns += 1

                elif re.search(r"[bcdfghjklmnpqrstvwxyz]{5,}", word.lower()) or re.search(r"(.)\1{4,}", word):
                    gibberish_patterns += 1

        return min(1.0, gibberish_patterns / max(total_checks, 1))


def enhance_benchmark_results_with_quality(results_file: Path, reference_texts_dir: Path | None = None) -> Path:
    """Enhance existing benchmark results with quality metrics."""
    with open(results_file, "rb") as f:
        results_data = msgspec.json.decode(f.read(), type=list[BenchmarkResult])

    results = results_data

    assessor = TextQualityAssessor()

    enhanced_results = []
    for result in results:
        enhanced_result = result

        if result.status == ExtractionStatus.SUCCESS and result.extracted_text:
            reference_text = None
            if reference_texts_dir:
                ref_file = reference_texts_dir / f"{Path(result.file_path).stem}.txt"
                if ref_file.exists():
                    reference_text = ref_file.read_text(encoding="utf-8", errors="ignore")

            quality_metrics = assessor.assess_extraction_quality(
                result.extracted_text, reference_text, Path(result.file_path)
            )

            enhanced_result = msgspec.structs.replace(
                result,
                quality_metrics=quality_metrics,
                overall_quality_score=_calculate_overall_quality_score(quality_metrics),
            )

        enhanced_results.append(enhanced_result)

    output_file = results_file.parent / f"enhanced_{results_file.name}"
    with open(output_file, "wb") as f:
        f.write(msgspec.json.encode(enhanced_results))

    return output_file


def _calculate_overall_quality_score(quality_metrics: dict[str, Any]) -> float:
    """Calculate overall quality score from individual metrics."""
    weights = {
        "extraction_completeness": 0.25,
        "text_coherence": 0.20,
        "semantic_similarity": 0.20,
        "format_specific_score": 0.15,
        "flesch_reading_ease": 0.10,
        "noise_ratio": -0.10,
    }

    score = 0.0
    total_weight = 0.0

    for metric, weight in weights.items():
        if metric in quality_metrics:
            value = quality_metrics[metric]

            if metric == "flesch_reading_ease":
                value = min(100, max(0, value)) / 100
            elif metric == "noise_ratio":
                value = 1 - value

            score += weight * value
            total_weight += abs(weight)

    return max(0.0, min(1.0, score / total_weight if total_weight > 0 else 0.0))
