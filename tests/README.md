# Tests Directory

This directory contains all test files and utilities for the PDF Search System.

## Test Structure

### Main Test Suites
- `test_quick.py` - **Recommended**: Robust, dependency-free comprehensive testing
- `test_simple.py` - Basic validation with minimal dependencies
- `test_comprehensive.py` - Professional-grade testing with external dependencies
- `test_advanced.py` - Enhanced testing with performance metrics
- `test_system.py` - System-level integration tests
- `test_table_pdf.py` - PDF table processing tests
- `test_table_simple.py` - Simple table functionality tests
- `test_table_validation.py` - Table processing validation

### Utilities Directory (`utilities/`)
- `validate_table_processing.py` - Comprehensive table processing validation
- `create_test_pdf.py` - Creates test PDF documents with table content

### Test Results
- Test result JSON files are saved to the project root directory
- Example: `test_results_quick.json`, `table_processing_validation_report.json`

### Generated Test Files
The following files are automatically created and persisted for reuse:
- `test_document_with_tables.pdf` - Table structure test PDF
- `table_validation_test_document.txt` - Table validation test data
- `table_simple_test_document.txt` - Simple table test data
- `table_test_document.pdf` - PDF with table content (in utilities/)

These files are reused across test runs to improve performance and consistency.

## Running Tests

### One Command Testing (Recommended)
The simplest way to run all tests:
```bash
cd tests/
python test.py
```

This single command:
- ✅ Automatically installs dependencies
- ✅ Runs all test suites sequentially 
- ✅ Shows progress and results in real-time
- ✅ Provides comprehensive summary
- ✅ Saves detailed results to JSON
- ✅ Works out of the box, no setup needed

### Individual Test Files
Run specific test suites directly:
```bash
cd tests/

python test_quick.py         # Quick comprehensive tests
python test_simple.py        # Basic tests  
python test_advanced.py      # Performance tests
python test_system.py        # System integration tests
```

### Using Makefile (Legacy)
From the tests directory:
```bash
cd tests/

# Run recommended test suite
make test

# Run specific test suites
make test-quick          # Quick comprehensive tests
make test-simple         # Basic tests
make test-all           # ALL tests with unified runner
make test-full           # Full test suite with dependencies
make test-tables         # Table processing validation

# Utility commands
make test-table-upload   # Create and upload test documents

# Docker management
make start               # Start all services
make stop                # Stop all services
make status              # Check service status
make clean               # Clean up containers
```

### Direct Execution
```bash
# Run individual test files
python3 test_quick.py
python3 test_simple.py
python3 test_comprehensive.py

# Run validation utilities
python3 utilities/validate_table_processing.py
python3 utilities/create_test_pdf.py
```

## Test Features

### Docker Service Validation
- Verifies all three services start correctly (API, Vector Store, Streamlit UI)
- Checks port accessibility (8000, 8001, 8501)
- Health checks and service communication

### API Endpoint Testing
- Document upload (`POST /upload-pdf`)
- Document search (`POST /search-doc`)
- Document listing (`GET /documents`)
- Document deletion (`DELETE /documents/{id}`)

### Table Processing Validation
- Tests table-aware PDF processing
- Validates that table rows are treated as single searchable units
- Verifies contextual search results

### System Integration
- End-to-end workflow testing
- Performance monitoring
- Error handling validation
- Service communication testing

## Test Dependencies

### No Dependencies (Recommended)
- `test_quick.py` - Uses only standard library
- `test_simple.py` - Minimal external dependencies

### With Dependencies
- `test_comprehensive.py` - Requires: pytest, docker, reportlab
- `test_advanced.py` - Requires: pytest, additional testing libraries

Install dependencies:
```bash
pip install -r ../test_requirements.txt
# or
make install-deps
```

## Output and Results

Tests save results to the project root directory:
- JSON result files for detailed analysis
- Console output with colored status indicators
- Performance metrics and timing data
- Error logs and debugging information

For more information, see `TESTING.md` and `IMPLEMENTATION_SUMMARY.md`.