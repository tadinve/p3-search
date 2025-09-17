# Test Results Directory

This directory contains structured test results for each test run of the PDF Search System.

## Directory Structure

Each test run creates a timestamped directory with the format: `run_YYYYMMDD_HHMMSS/`

### Contents of Each Run Directory

Each run directory contains:

- **`test_summary.json`** - Complete test results in JSON format for programmatic access
- **`test_detailed_results.txt`** - Human-readable detailed summary of the test run
- **`test_[name]_output.txt`** - Individual output files for each test (8 files total)

### Individual Test Output Files

Each test produces its own output file:
1. `test_quick_output.txt` - Quick Comprehensive Test
2. `test_simple_output.txt` - Simple Validation Test  
3. `test_advanced_output.txt` - Advanced Performance Test
4. `test_system_output.txt` - System Integration Test
5. `test_comprehensive_output.txt` - Comprehensive Professional Test
6. `test_table_pdf_output.txt` - Table PDF Processing
7. `test_table_simple_output.txt` - Table Simple Functionality
8. `test_table_validation_output.txt` - Table Validation

## JSON Summary Format

The `test_summary.json` contains:
- Run metadata (timestamp, directory, duration)
- Overall results (total/passed/failed/skipped counts)
- Individual test results with success status, duration, and output file paths

## Usage

To view results from the latest test run:
```bash
# Find the latest run directory
ls -la results/ | tail -1

# View the summary  
cat results/run_YYYYMMDD_HHMMSS/test_detailed_results.txt

# View specific test output
cat results/run_YYYYMMDD_HHMMSS/test_quick_output.txt
```

## Automation

This structured format enables:
- Easy result archival and comparison
- Automated result processing and reporting
- Historical test trend analysis
- CI/CD integration for result tracking