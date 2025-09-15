from src.config_defaults import DefaultValues, LanguageMapper


class TestDefaultValues:
    def test_timeout_values(self):
        assert DefaultValues.EXTRACTION_TIMEOUT_SECONDS == 1800
        assert DefaultValues.MAX_RUN_DURATION_MINUTES == 30
        assert isinstance(DefaultValues.EXTRACTION_TIMEOUT_SECONDS, int)
        assert isinstance(DefaultValues.MAX_RUN_DURATION_MINUTES, int)

    def test_benchmark_defaults(self):
        assert DefaultValues.DEFAULT_ITERATIONS == 3
        assert DefaultValues.DEFAULT_WARMUP_RUNS == 1
        assert DefaultValues.COOLDOWN_SECONDS == 5
        assert DefaultValues.MAX_RETRIES == 3

    def test_performance_monitoring_defaults(self):
        assert DefaultValues.SAMPLING_INTERVAL_MS == 50
        assert isinstance(DefaultValues.SAMPLING_INTERVAL_MS, int)

    def test_resource_limits(self):
        assert DefaultValues.MAX_MEMORY_MB == 4096
        assert DefaultValues.MAX_CPU_PERCENT == 800
        assert DefaultValues.MAX_CONCURRENT_FILES == 1

    def test_framework_specific_defaults(self):
        assert DefaultValues.KREUZBERG_CACHE_DISABLED is True
        assert DefaultValues.TEXT_PREVIEW_LENGTH == 200

    def test_all_defaults_are_reasonable(self):
        assert 0 < DefaultValues.EXTRACTION_TIMEOUT_SECONDS <= 3600
        assert 0 < DefaultValues.MAX_RUN_DURATION_MINUTES <= 120

        assert DefaultValues.SAMPLING_INTERVAL_MS > 0
        assert DefaultValues.COOLDOWN_SECONDS >= 0

        assert DefaultValues.MAX_MEMORY_MB >= 1024
        assert DefaultValues.MAX_CPU_PERCENT > 0


class TestLanguageMapper:
    def test_tesseract_mapping_completeness(self):
        mapping = LanguageMapper.TESSERACT_MAPPING

        required_languages = ["eng", "deu", "heb", "chi_sim", "jpn", "kor"]
        for lang in required_languages:
            assert lang in mapping, f"Missing {lang} in Tesseract mapping"

        assert mapping["eng"] == "eng"
        assert mapping["deu"] == "deu"
        assert mapping["heb"] == "heb"

    def test_easyocr_mapping_completeness(self):
        mapping = LanguageMapper.EASYOCR_MAPPING

        required_languages = ["eng", "deu", "heb", "chi_sim", "jpn", "kor"]
        for lang in required_languages:
            assert lang in mapping, f"Missing {lang} in EasyOCR mapping"

        assert mapping["eng"] == "en"
        assert mapping["deu"] == "de"
        assert mapping["heb"] == "he"

    def test_paddleocr_mapping_completeness(self):
        mapping = LanguageMapper.PADDLEOCR_MAPPING

        required_languages = ["eng", "deu", "heb", "chi_sim", "jpn", "kor"]
        for lang in required_languages:
            assert lang in mapping, f"Missing {lang} in PaddleOCR mapping"

        assert mapping["eng"] == "en"
        assert mapping["deu"] == "german"
        assert mapping["chi_sim"] == "ch"

    def test_mapping_consistency(self):
        tesseract_keys = set(LanguageMapper.TESSERACT_MAPPING.keys())
        easyocr_keys = set(LanguageMapper.EASYOCR_MAPPING.keys())
        paddleocr_keys = set(LanguageMapper.PADDLEOCR_MAPPING.keys())

        assert tesseract_keys == easyocr_keys == paddleocr_keys

    def test_get_mapping_method(self):
        tesseract_mapping = LanguageMapper.get_mapping("tesseract")
        assert tesseract_mapping == LanguageMapper.TESSERACT_MAPPING

        easyocr_mapping = LanguageMapper.get_mapping("easyocr")
        assert easyocr_mapping == LanguageMapper.EASYOCR_MAPPING

        paddleocr_mapping = LanguageMapper.get_mapping("paddleocr")
        assert paddleocr_mapping == LanguageMapper.PADDLEOCR_MAPPING

    def test_get_mapping_case_insensitive(self):
        mapping = LanguageMapper.get_mapping("TESSERACT")
        assert mapping == LanguageMapper.TESSERACT_MAPPING

        mapping = LanguageMapper.get_mapping("EasyOCR")
        assert mapping == LanguageMapper.EASYOCR_MAPPING

    def test_get_mapping_fallback(self):
        unknown_mapping = LanguageMapper.get_mapping("unknown_backend")
        assert unknown_mapping == LanguageMapper.TESSERACT_MAPPING

    def test_mapping_values_are_strings(self):
        for backend_name in ["tesseract", "easyocr", "paddleocr"]:
            mapping = LanguageMapper.get_mapping(backend_name)

            for input_lang, output_lang in mapping.items():
                assert isinstance(input_lang, str), f"Input language {input_lang} is not string"
                assert isinstance(output_lang, str), f"Output language {output_lang} is not string"
                assert len(output_lang) > 0, f"Empty output language for {input_lang}"

    def test_hebrew_fallback_in_paddleocr(self):
        mapping = LanguageMapper.PADDLEOCR_MAPPING
        assert mapping["heb"] == "en"

    def test_language_mapping_uniqueness(self):
        for backend_name in ["tesseract", "easyocr", "paddleocr"]:
            mapping = LanguageMapper.get_mapping(backend_name)

            input_langs = list(mapping.keys())
            assert len(input_langs) == len(set(input_langs)), f"Duplicate keys in {backend_name} mapping"


class TestConfigurationIntegration:
    def test_timeout_consistency(self):
        from src.config_defaults import DefaultValues

        assert DefaultValues.EXTRACTION_TIMEOUT_SECONDS == 1800
        assert DefaultValues.MAX_RUN_DURATION_MINUTES == 30

    def test_language_mapper_backend_names(self):
        expected_backends = ["tesseract", "easyocr", "paddleocr"]

        for backend in expected_backends:
            mapping = LanguageMapper.get_mapping(backend)
            assert isinstance(mapping, dict)
            assert len(mapping) > 0

    def test_default_values_types(self):
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
