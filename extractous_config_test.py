"""Test different Extractous configurations for optimization."""

import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from src.extractors import ExtractousExtractor


def test_speed_optimized():
    """Test speed-optimized configuration."""
    print("\n=== Testing Speed-Optimized Configuration ===")
    extractor = ExtractousExtractor()
    extractor.extractor.set_extract_string_max_length(1000000)

    test_files = [
        "test_documents/pdfs/sample.pdf",
        "test_documents/office/sample.docx",
        "test_documents/html/sample.html",
    ]

    total_time = 0
    success_count = 0

    for file_path in test_files:
        if Path(file_path).exists():
            try:
                start = time.time()
                text = extractor.extract_text(str(file_path))
                elapsed = time.time() - start
                total_time += elapsed
                if text:
                    success_count += 1
                    print(f"✓ {file_path}: {len(text)} chars in {elapsed:.2f}s")
                else:
                    print(f"✗ {file_path}: Failed")
            except Exception as e:
                print(f"✗ {file_path}: Error - {e}")

    print(f"\nSpeed-optimized: {success_count}/{len(test_files)} successful, Total: {total_time:.2f}s")
    return total_time, success_count


def test_quality_optimized():
    """Test quality-optimized configuration."""
    print("\n=== Testing Quality-Optimized Configuration ===")
    extractor = ExtractousExtractor()
    extractor.extractor.set_extract_string_max_length(10000000)

    test_files = [
        "test_documents/pdfs/sample.pdf",
        "test_documents/office/sample.docx",
        "test_documents/html/sample.html",
    ]

    total_time = 0
    success_count = 0
    total_chars = 0

    for file_path in test_files:
        if Path(file_path).exists():
            try:
                start = time.time()
                text = extractor.extract_text(str(file_path))
                elapsed = time.time() - start
                total_time += elapsed
                if text:
                    success_count += 1
                    total_chars += len(text)
                    print(f"✓ {file_path}: {len(text)} chars in {elapsed:.2f}s")
                else:
                    print(f"✗ {file_path}: Failed")
            except Exception as e:
                print(f"✗ {file_path}: Error - {e}")

    print(
        f"\nQuality-optimized: {success_count}/{len(test_files)} successful, Total: {total_time:.2f}s, Chars: {total_chars}"
    )
    return total_time, success_count, total_chars


def test_balanced():
    """Test balanced configuration (current default)."""
    print("\n=== Testing Balanced Configuration ===")
    extractor = ExtractousExtractor()

    test_files = [
        "test_documents/pdfs/sample.pdf",
        "test_documents/office/sample.docx",
        "test_documents/html/sample.html",
    ]

    total_time = 0
    success_count = 0
    total_chars = 0

    for file_path in test_files:
        if Path(file_path).exists():
            try:
                start = time.time()
                text = extractor.extract_text(str(file_path))
                elapsed = time.time() - start
                total_time += elapsed
                if text:
                    success_count += 1
                    total_chars += len(text)
                    print(f"✓ {file_path}: {len(text)} chars in {elapsed:.2f}s")
                else:
                    print(f"✗ {file_path}: Failed")
            except Exception as e:
                print(f"✗ {file_path}: Error - {e}")

    print(f"\nBalanced: {success_count}/{len(test_files)} successful, Total: {total_time:.2f}s, Chars: {total_chars}")
    return total_time, success_count, total_chars


if __name__ == "__main__":
    print("Testing Extractous configurations...")

    speed_time, speed_success = test_speed_optimized()
    quality_time, quality_success, quality_chars = test_quality_optimized()
    balanced_time, balanced_success, balanced_chars = test_balanced()

    print("\n=== COMPARISON ===")
    print(f"Speed-optimized: {speed_time:.2f}s, {speed_success} successful")
    print(f"Quality-optimized: {quality_time:.2f}s, {quality_success} successful, {quality_chars} chars")
    print(f"Balanced: {balanced_time:.2f}s, {balanced_success} successful, {balanced_chars} chars")

    if quality_success > balanced_success:
        print("\n➜ RECOMMENDATION: Quality-optimized (10MB limit) - Better extraction")
    elif speed_time < balanced_time * 0.7 and speed_success == balanced_success:
        print("\n➜ RECOMMENDATION: Speed-optimized (1MB limit) - Significantly faster")
    else:
        print("\n➜ RECOMMENDATION: Balanced (5MB limit) - Good balance")
