______________________________________________________________________

## title: Download Raw Data

# Download Raw Data

## Available CSV Files

- [**Full Results**](full-results.csv) - Complete benchmark results with all metrics
- [**By File Type Summary**](by-file-type.csv) - Aggregated results by file type
- [**By File Size Summary**](by-file-size.csv) - Aggregated results by file size

## Data Dictionary

### Full Results CSV

| Column                | Description                                |
| --------------------- | ------------------------------------------ |
| framework             | Framework name                             |
| file_path             | Path to test file                          |
| file_type             | File extension                             |
| file_size             | File size in bytes                         |
| category              | Size category                              |
| status                | Extraction status (SUCCESS/FAILED/TIMEOUT) |
| extraction_time       | Time in seconds                            |
| peak_memory_mb        | Peak memory usage in MB                    |
| avg_memory_mb         | Average memory usage in MB                 |
| peak_cpu_percent      | Peak CPU usage percentage                  |
| character_count       | Extracted text character count             |
| word_count            | Extracted text word count                  |
| overall_quality_score | Quality assessment score (0-100)           |
| error_message         | Error details if failed                    |

## Usage

These CSV files can be imported into Excel, Google Sheets, or any data analysis tool for further analysis.
