"""Tests for configuration defaults module."""

from src.config_defaults import DefaultValues, LanguageMapper


class TestDefaultValues:
    """Test centralized default values."""

    def test_timeout_values(self):
        """Test timeout-related default values."""
        assert DefaultValues.EXTRACTION_TIMEOUT_SECONDS == 1800
        assert DefaultValues.MAX_RUN_DURATION_MINUTES == 30
        assert isinstance(DefaultValues.EXTRACTION_TIMEOUT_SECONDS, int)
        assert isinstance(DefaultValues.MAX_RUN_DURATION_MINUTES, int)

    def test_benchmark_defaults(self):
        """Test benchmark execution default values."""
        assert DefaultValues.DEFAULT_ITERATIONS == 3
        assert DefaultValues.DEFAULT_WARMUP_RUNS == 1
        assert DefaultValues.COOLDOWN_SECONDS == 5
        assert DefaultValues.MAX_RETRIES == 3

    def test_performance_monitoring_defaults(self):
        """Test performance monitoring default values."""
        assert DefaultValues.SAMPLING_INTERVAL_MS == 50
        assert isinstance(DefaultValues.SAMPLING_INTERVAL_MS, int)

    def test_resource_limits(self):
        """Test resource limit default values."""
        assert DefaultValues.MAX_MEMORY_MB == 4096
        assert DefaultValues.MAX_CPU_PERCENT == 800
        assert DefaultValues.MAX_CONCURRENT_FILES == 1

    def test_framework_specific_defaults(self):
        """Test framework-specific default values."""
        assert DefaultValues.KREUZBERG_CACHE_DISABLED is True
        assert DefaultValues.TEXT_PREVIEW_LENGTH == 200

    def test_all_defaults_are_reasonable(self):
        """Test that all default values are within reasonable ranges."""
        assert 0 < DefaultValues.EXTRACTION_TIMEOUT_SECONDS <= 3600
        assert 0 < DefaultValues.MAX_RUN_DURATION_MINUTES <= 120

        assert DefaultValues.SAMPLING_INTERVAL_MS > 0
        assert DefaultValues.COOLDOWN_SECONDS >= 0

        assert DefaultValues.MAX_MEMORY_MB >= 1024
        assert DefaultValues.MAX_CPU_PERCENT > 0


class TestLanguageMapper:
    """Test language mapping configurations."""

    def test_tesseract_mapping_completeness(self):
        """Test that Tesseract mapping has all required languages."""
        mapping = LanguageMapper.TESSERACT_MAPPING

        required_languages = ["eng", "deu", "heb", "chi_sim", "jpn", "kor"]
        for lang in required_languages:
            assert lang in mapping, f"Missing {lang} in Tesseract mapping"

        assert mapping["eng"] == "eng"
        assert mapping["deu"] == "deu"
        assert mapping["heb"] == "heb"

    def test_easyocr_mapping_completeness(self):
        """Test that EasyOCR mapping has all required languages."""
        mapping = LanguageMapper.EASYOCR_MAPPING

        required_languages = ["eng", "deu", "heb", "chi_sim", "jpn", "kor"]
        for lang in required_languages:
            assert lang in mapping, f"Missing {lang} in EasyOCR mapping"

        assert mapping["eng"] == "en"
        assert mapping["deu"] == "de"
        assert mapping["heb"] == "he"

    def test_paddleocr_mapping_completeness(self):
        """Test that PaddleOCR mapping has all required languages."""
        mapping = LanguageMapper.PADDLEOCR_MAPPING

        required_languages = ["eng", "deu", "heb", "chi_sim", "jpn", "kor"]
        for lang in required_languages:
            assert lang in mapping, f"Missing {lang} in PaddleOCR mapping"

        assert mapping["eng"] == "en"
        assert mapping["deu"] == "german"
        assert mapping["chi_sim"] == "ch"

    def test_mapping_consistency(self):
        """Test that all mappings have the same input languages."""
        tesseract_keys = set(LanguageMapper.TESSERACT_MAPPING.keys())
        easyocr_keys = set(LanguageMapper.EASYOCR_MAPPING.keys())
        paddleocr_keys = set(LanguageMapper.PADDLEOCR_MAPPING.keys())

        assert tesseract_keys == easyocr_keys == paddleocr_keys

    def test_get_mapping_method(self):
        """Test the get_mapping class method."""
        tesseract_mapping = LanguageMapper.get_mapping("tesseract")
        assert tesseract_mapping == LanguageMapper.TESSERACT_MAPPING

        easyocr_mapping = LanguageMapper.get_mapping("easyocr")
        assert easyocr_mapping == LanguageMapper.EASYOCR_MAPPING

        paddleocr_mapping = LanguageMapper.get_mapping("paddleocr")
        assert paddleocr_mapping == LanguageMapper.PADDLEOCR_MAPPING

    def test_get_mapping_case_insensitive(self):
        """Test that get_mapping handles case variations."""
        mapping = LanguageMapper.get_mapping("TESSERACT")
        assert mapping == LanguageMapper.TESSERACT_MAPPING

        mapping = LanguageMapper.get_mapping("EasyOCR")
        assert mapping == LanguageMapper.EASYOCR_MAPPING

    def test_get_mapping_fallback(self):
        """Test that get_mapping falls back to Tesseract for unknown backends."""
        unknown_mapping = LanguageMapper.get_mapping("unknown_backend")
        assert unknown_mapping == LanguageMapper.TESSERACT_MAPPING

    def test_mapping_values_are_strings(self):
        """Test that all mapping values are valid strings."""
        for backend_name in ["tesseract", "easyocr", "paddleocr"]:
            mapping = LanguageMapper.get_mapping(backend_name)

            for input_lang, output_lang in mapping.items():
                assert isinstance(input_lang, str), f"Input language {input_lang} is not string"
                assert isinstance(output_lang, str), f"Output language {output_lang} is not string"
                assert len(output_lang) > 0, f"Empty output language for {input_lang}"

    def test_hebrew_fallback_in_paddleocr(self):
        """Test that Hebrew falls back to English in PaddleOCR (unsupported)."""
        mapping = LanguageMapper.PADDLEOCR_MAPPING
        assert mapping["heb"] == "en"

    def test_language_mapping_uniqueness(self):
        """Test that language mappings don't have unexpected duplicates."""
        for backend_name in ["tesseract", "easyocr", "paddleocr"]:
            mapping = LanguageMapper.get_mapping(backend_name)

            input_langs = list(mapping.keys())
            assert len(input_langs) == len(set(input_langs)), f"Duplicate keys in {backend_name} mapping"


class TestConfigurationIntegration:
    """Test integration between different configuration components."""

    def test_timeout_consistency(self):
        """Test that timeout values are consistent across the system."""
        from src.config_defaults import DefaultValues

        assert DefaultValues.EXTRACTION_TIMEOUT_SECONDS == 1800
        assert DefaultValues.MAX_RUN_DURATION_MINUTES == 30

    def test_language_mapper_backend_names(self):
        """Test that language mapper backend names match expected values."""
        expected_backends = ["tesseract", "easyocr", "paddleocr"]

        for backend in expected_backends:
            mapping = LanguageMapper.get_mapping(backend)
            assert isinstance(mapping, dict)
            assert len(mapping) > 0

    def test_default_values_types(self):
        """Test that all default values have correct types."""
        int_values = [
            DefaultValues.EXTRACTION_TIMEOUT_SECONDS,
            DefaultValues.MAX_RUN_DURATION_MINUTES,
            DefaultValues.DEFAULT_ITERATIONS,
            DefaultValues.DEFAULT_WARMUP_RUNS,
            DefaultValues.COOLDOWN_SECONDS,
            DefaultValues.SAMPLING_INTERVAL_MS,
            DefaultValues.MAX_RETRIES,
            DefaultValues.MAX_MEMORY_MB,
            DefaultValues.MAX_CPU_PERCENT,
            DefaultValues.MAX_CONCURRENT_FILES,
            DefaultValues.TEXT_PREVIEW_LENGTH,
        ]

        for value in int_values:
            assert isinstance(value, int), f"Expected int, got {type(value)}"

        bool_values = [
            DefaultValues.KREUZBERG_CACHE_DISABLED,
        ]

        for value in bool_values:
            assert isinstance(value, bool), f"Expected bool, got {type(value)}"
