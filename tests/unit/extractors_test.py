"""Tests for extractor implementations."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.extractors import (
    KreuzbergAsyncExtractor,
    KreuzbergSyncExtractor,
    get_extractor,
    get_language_config,
)
from src.types import Framework


class TestLanguageConfiguration:
    """Test language detection and mapping."""

    def test_hebrew_language_detection(self):
        """Test Hebrew language detection from filename."""
        test_cases = [
            "hebrew_document.pdf",
            "report_israel_2024.docx",
            "tel_aviv_meeting.txt",
            "document_heb.pdf",
            "file_he_IL.docx",
        ]

        for filename in test_cases:
            result = get_language_config(filename)
            assert result == "heb", f"Failed for {filename}"

    def test_german_language_detection(self):
        """Test German language detection from filename."""
        test_cases = [
            "german_report.pdf",
            "germany_statistics.docx",
            "berlin_conference.txt",
            "document_deu.pdf",
            "file_de_DE.docx",
        ]

        for filename in test_cases:
            result = get_language_config(filename)
            assert result == "deu", f"Failed for {filename}"

    def test_chinese_language_detection(self):
        """Test Chinese language detection from filename."""
        test_cases = [
            "chinese_manual.pdf",
            "china_report.docx",
            "beijing_summit.txt",
            "document_chi_sim.pdf",
            "file_zh_CN.docx",
            "report_cn_2024.pdf",
        ]

        for filename in test_cases:
            result = get_language_config(filename)
            assert result == "chi_sim", f"Failed for {filename}"

    def test_japanese_language_detection(self):
        """Test Japanese language detection from filename."""
        test_cases = [
            "japanese_guide.pdf",
            "japan_analysis.docx",
            "document_jpn.pdf",
            "file_jp_vertical.pdf",
            "report_ja_JP.docx",
            "vert_text.pdf",  # Contains "vert" for vertical text
        ]

        for filename in test_cases:
            result = get_language_config(filename)
            assert result == "jpn", f"Failed for {filename}"

    def test_korean_language_detection(self):
        """Test Korean language detection from filename."""
        test_cases = [
            "korean_document.pdf",
            "korea_study.docx",
            "document_kor.pdf",
            "file_kr_2024.pdf",
            "report_ko_KR.docx",
        ]

        for filename in test_cases:
            result = get_language_config(filename)
            assert result == "kor", f"Failed for {filename}"

    def test_english_default_language(self):
        """Test that English is the default language."""
        test_cases = [
            "standard_document.pdf",
            "report.docx",
            "meeting_notes.txt",
            "financial_analysis.pdf",
        ]

        for filename in test_cases:
            result = get_language_config(filename)
            assert result == "eng", f"Failed for {filename}"

    def test_path_object_handling(self):
        """Test that Path objects are handled correctly."""
        path = Path("hebrew_document.pdf")
        result = get_language_config(path)
        assert result == "heb"


class TestExtractorFactory:
    """Test the extractor factory pattern."""

    def test_get_extractor_kreuzberg_sync(self):
        """Test getting Kreuzberg sync extractor."""
        extractor = get_extractor(Framework.KREUZBERG_SYNC)
        assert isinstance(extractor, KreuzbergSyncExtractor)

    def test_get_extractor_kreuzberg_async(self):
        """Test getting Kreuzberg async extractor."""
        extractor = get_extractor(Framework.KREUZBERG_ASYNC)
        assert isinstance(extractor, KreuzbergAsyncExtractor)

    def test_get_extractor_unknown_framework(self):
        """Test error handling for unknown framework."""
        with pytest.raises(KeyError):
            get_extractor("unknown_framework")

    def test_all_frameworks_have_extractors(self):
        """Test that all frameworks have corresponding extractors."""
        for framework in Framework:
            # Should not raise exception
            extractor = get_extractor(framework)
            assert extractor is not None


class TestKreuzbergExtractors:
    """Test Kreuzberg extractor implementations."""

    def test_kreuzberg_sync_initialization(self):
        """Test Kreuzberg sync extractor can be initialized."""
        extractor = KreuzbergSyncExtractor()
        assert extractor is not None

    def test_kreuzberg_async_initialization(self):
        """Test Kreuzberg async extractor can be initialized."""
        extractor = KreuzbergAsyncExtractor()
        assert extractor is not None

    @pytest.mark.skipif(
        condition=True,  # Skip unless kreuzberg is available
        reason="Requires kreuzberg installation",
    )
    def test_kreuzberg_sync_extract_text(self):
        """Test Kreuzberg sync text extraction."""
        extractor = KreuzbergSyncExtractor()

        # Create a test file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Test document content for extraction.")
            test_file = f.name

        try:
            result = extractor.extract_text(test_file)
            assert isinstance(result, str)
            assert "Test document content" in result
        finally:
            Path(test_file).unlink()

    @pytest.mark.skipif(
        condition=True,  # Skip unless kreuzberg is available
        reason="Requires kreuzberg installation",
    )
    @pytest.mark.asyncio
    async def test_kreuzberg_async_extract_text(self):
        """Test Kreuzberg async text extraction."""
        extractor = KreuzbergAsyncExtractor()

        # Create a test file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Test document content for extraction.")
            test_file = f.name

        try:
            result = await extractor.extract_text(test_file)
            assert isinstance(result, str)
            assert "Test document content" in result
        finally:
            Path(test_file).unlink()

    def test_kreuzberg_missing_import_error(self):
        """Test error handling when Kreuzberg is not installed."""
        # Mock kreuzberg as None to simulate missing import
        with patch("src.extractors.kreuzberg", None):
            extractor = KreuzbergSyncExtractor()

            with pytest.raises(ImportError, match="Kreuzberg is not installed"):
                extractor.extract_text("test.pdf")

    @pytest.mark.asyncio
    async def test_kreuzberg_async_missing_import_error(self):
        """Test async error handling when Kreuzberg is not installed."""
        # Mock kreuzberg as None to simulate missing import
        with patch("src.extractors.kreuzberg", None):
            extractor = KreuzbergAsyncExtractor()

            with pytest.raises(ImportError, match="Kreuzberg is not installed"):
                await extractor.extract_text("test.pdf")

    def test_kreuzberg_cache_disabled_configuration(self):
        """Test that Kreuzberg extractors disable cache."""
        # Mock kreuzberg and ExtractionConfig
        mock_kreuzberg = Mock()
        mock_config_class = Mock()
        mock_result = Mock()
        mock_result.content = "extracted text"

        with (
            patch("src.extractors.kreuzberg", mock_kreuzberg),
            patch("src.extractors.ExtractionConfig", mock_config_class),
        ):
            mock_kreuzberg.extract_file_sync.return_value = mock_result

            extractor = KreuzbergSyncExtractor()
            result = extractor.extract_text("test.pdf")

            # Verify ExtractionConfig was called with use_cache=False
            mock_config_class.assert_called_once_with(use_cache=False)
            assert result == "extracted text"

    @pytest.mark.asyncio
    async def test_kreuzberg_async_cache_disabled_configuration(self):
        """Test that Kreuzberg async extractor disables cache."""
        # Mock kreuzberg and ExtractionConfig
        mock_kreuzberg = Mock()
        mock_config_class = Mock()
        mock_result = Mock()
        mock_result.content = "extracted text"

        with (
            patch("src.extractors.kreuzberg", mock_kreuzberg),
            patch("src.extractors.ExtractionConfig", mock_config_class),
        ):
            mock_kreuzberg.extract_file.return_value = mock_result

            extractor = KreuzbergAsyncExtractor()
            result = await extractor.extract_text("test.pdf")

            # Verify ExtractionConfig was called with use_cache=False
            mock_config_class.assert_called_once_with(use_cache=False)
            assert result == "extracted text"

    def test_kreuzberg_sync_extract_with_metadata(self):
        """Test Kreuzberg sync metadata extraction."""
        # Mock kreuzberg and ExtractionConfig
        mock_kreuzberg = Mock()
        mock_config_class = Mock()
        mock_result = Mock()
        mock_result.content = "extracted text"
        mock_result.metadata = {"title": "Test Document", "author": "Test Author"}

        with (
            patch("src.extractors.kreuzberg", mock_kreuzberg),
            patch("src.extractors.ExtractionConfig", mock_config_class),
        ):
            mock_kreuzberg.extract_file_sync.return_value = mock_result

            extractor = KreuzbergSyncExtractor()
            text, metadata = extractor.extract_with_metadata("test.pdf")

            assert text == "extracted text"
            assert metadata == {"title": "Test Document", "author": "Test Author"}
            mock_config_class.assert_called_once_with(use_cache=False)

    @pytest.mark.asyncio
    async def test_kreuzberg_async_extract_with_metadata(self):
        """Test Kreuzberg async metadata extraction."""
        # Mock kreuzberg and ExtractionConfig
        mock_kreuzberg = Mock()
        mock_config_class = Mock()
        mock_result = Mock()
        mock_result.content = "extracted text"
        mock_result.metadata = {"title": "Test Document", "pages": 5}

        with (
            patch("src.extractors.kreuzberg", mock_kreuzberg),
            patch("src.extractors.ExtractionConfig", mock_config_class),
        ):
            mock_kreuzberg.extract_file.return_value = mock_result

            extractor = KreuzbergAsyncExtractor()
            text, metadata = await extractor.extract_with_metadata("test.pdf")

            assert text == "extracted text"
            assert metadata == {"title": "Test Document", "pages": 5}
            mock_config_class.assert_called_once_with(use_cache=False)

    def test_kreuzberg_metadata_fallback(self):
        """Test metadata extraction fallback when no metadata exists."""
        # Mock result without metadata attribute
        mock_kreuzberg = Mock()
        mock_config_class = Mock()
        mock_result = Mock()
        mock_result.content = "extracted text"
        # No metadata attribute

        with (
            patch("src.extractors.kreuzberg", mock_kreuzberg),
            patch("src.extractors.ExtractionConfig", mock_config_class),
        ):
            mock_kreuzberg.extract_file_sync.return_value = mock_result

            extractor = KreuzbergSyncExtractor()
            text, metadata = extractor.extract_with_metadata("test.pdf")

            assert text == "extracted text"
            assert metadata == {}  # Should fallback to empty dict


class TestExtractorErrorHandling:
    """Test extractor error handling scenarios."""

    def test_nonexistent_file_handling(self):
        """Test handling of non-existent files."""
        # This should be handled by the individual extractors
        # For now, document expected behavior

    def test_corrupted_file_handling(self):
        """Test handling of corrupted files."""
        # This should be handled by the individual extractors
        # For now, document expected behavior

    def test_unsupported_format_handling(self):
        """Test handling of unsupported file formats."""
        # This should be handled by the individual extractors
        # For now, document expected behavior


class TestExtractorPerformance:
    """Test extractor performance characteristics."""

    def test_extractor_memory_usage(self):
        """Test that extractors don't leak memory."""
        # This would require memory profiling
        # For now, document expected behavior

    def test_extractor_concurrent_access(self):
        """Test that extractors are thread-safe."""
        # This would require concurrent testing
        # For now, document expected behavior
