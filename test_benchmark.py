from pathlib import Path

import msgspec

from src.types import BenchmarkResult, DocumentCategory, ExtractionStatus, FileType, Framework

results = []

test_files = [
    ("test_documents/office/word_tables.docx", FileType.DOCX, 16404),
    ("test_documents/office/unit_test_lists.docx", FileType.DOCX, 12345),
    ("test_documents/office/fake.docx", FileType.DOCX, 8765),
]

frameworks = [Framework.KREUZBERG_SYNC, Framework.EXTRACTOUS, Framework.MARKITDOWN]

for framework in frameworks:
    for file_path, file_type, file_size in test_files:
        result = BenchmarkResult(
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            category=DocumentCategory.OFFICE,
            framework=framework,
            iteration=1,
            extraction_time=0.5 + (file_size / 50000),
            peak_memory_mb=50 + (file_size / 1000),
            avg_memory_mb=40 + (file_size / 1000),
            peak_cpu_percent=30 + (file_size / 500),
            avg_cpu_percent=20 + (file_size / 600),
            status=ExtractionStatus.SUCCESS,
            character_count=file_size * 2,
            word_count=file_size // 5,
            quality_metrics={"readability": 75.5, "completeness": 0.95, "coherence": 0.88},
            overall_quality_score=0.85,
            extracted_text="Sample extracted text..." if framework == Framework.KREUZBERG_SYNC else "Different text...",
            attempts=1,
        )
        results.append(result)

output_dir = Path("results")
output_dir.mkdir(exist_ok=True)

encoder = msgspec.json.Encoder()
with open(output_dir / "results.json", "wb") as f:
    f.write(encoder.encode(results))

print(f"✅ Generated {len(results)} benchmark results")
print(f"   Frameworks: {len(frameworks)}")
print(f"   Files: {len(test_files)}")
print(f"   Total results: {len(results)}")
