# PDF Search System - Testing Guide

This document provides comprehensive testing instructions for the PDF Search System.

## 🧪 Test Suites Available

### 1. Simple Test Suite (`tests/test_simple.py`)
- **Purpose**: Basic system validation without external dependencies
- **Features**: Docker health checks, API endpoint testing, document operations
- **Dependencies**: None (uses only standard library and requests)
- **Runtime**: ~30-60 seconds

### 2. Advanced Test Suite (`tests/test_advanced.py`) 
- **Purpose**: Enhanced testing with intermediate dependencies
- **Features**: More thorough validation, performance metrics, error simulation  
- **Dependencies**: pytest, additional testing libraries
- **Runtime**: ~1-3 minutes

### 3. Comprehensive Test Suite (`tests/test_comprehensive.py`)
- **Purpose**: Professional-grade testing with external libraries
- **Coverage**: Complete system validation, performance metrics, detailed reporting
- **Requirements**: pytest, requests, docker, reportlab
- **Runtime**: ~10-15 minutes

## 🚀 Quick Start Testing

### Option 1: Using Make (Recommended)
```bash
# Run simple test suite
make test

# Run comprehensive test suite (installs dependencies)
make test-full

# Start services and run quick verification
make dev-setup
make verify
```

### Option 2: Direct Python Execution
```bash
```bash
# Simple test suite (no dependencies required)
python3 tests/test_simple.py

# Advanced test suite (requires some dependencies)
python3 tests/test_advanced.py

# Comprehensive test suite (requires all dependencies)
python3 tests/test_comprehensive.py
```

## 📋 Test Coverage

### System Infrastructure Tests
- ✅ Docker Compose service startup
- ✅ Service health checks on correct ports
- ✅ API endpoint accessibility
- ✅ Service interdependency validation

### API Functionality Tests
- ✅ Document upload (PDF files)
- ✅ Document listing with metadata
- ✅ Document search with similarity scoring
- ✅ Individual document deletion
- ✅ Bulk document deletion
- ✅ Error handling and edge cases

### Document Processing Tests
- ✅ Text extraction from PDFs
- ✅ Table detection and row processing
- ✅ Vector embedding generation
- ✅ Search result accuracy
- ✅ Table content search (complete rows)

### Integration Tests
- ✅ End-to-end document lifecycle
- ✅ Search result consistency
- ✅ Service communication validation
- ✅ Data persistence verification

## 🎯 Expected Results

### Service Health
All three services should start and be accessible:
- **API Backend**: http://localhost:8000 (FastAPI docs)
- **Vector Store**: http://localhost:8001 (FastAPI docs)  
- **Streamlit UI**: http://localhost:8501 (Web interface)

### Document Operations
- Upload: PDF files should be processed and stored
- List: All uploaded documents should appear in listings
- Search: Relevant results should be returned with similarity scores
- Delete: Documents should be removable individually or in bulk

### Table Processing
- Table rows should be extracted as complete units
- Searching for table data should return entire rows
- Results should include `[TABLE]` prefix for table content

## 🔧 Test Configuration

### Timeouts
- Service startup: 120 seconds
- Health checks: 60 seconds
- API requests: 30 seconds

### Ports Validated
- API Backend: 8000
- Vector Store: 8001
- Streamlit UI: 8501

### Search Parameters
- Default limit: 10 results
- Minimum similarity: 0.5 (adjustable for testing)
- Query timeout: 30 seconds

## 📊 Test Output

### Success Indicators
```
✅ Docker Services Start:     PASS
✅ Services Health:           PASS  
✅ Document Upload:           PASS (100% success)
✅ Document Listing:          PASS
✅ Search Functionality:      PASS (80% success)
✅ Document Deletion:         PASS
🎉 OVERALL STATUS: ALL TESTS PASSED
```

### Failure Indicators
```
❌ Docker Services Start:     FAIL
❌ Services Health:           FAIL
⚠️  OVERALL STATUS: SOME TESTS FAILED
```

## 🐛 Troubleshooting

### Common Issues

1. **Services Won't Start**
   ```bash
   # Check Docker daemon
   docker info
   
   # Clean up existing containers
   make clean
   
   # Restart services
   make start
   ```

2. **Port Conflicts**
   ```bash
   # Check what's using the ports
   lsof -i :8000 -i :8001 -i :8501
   
   # Kill conflicting processes
   sudo lsof -ti:8000 | xargs kill -9
   ```

3. **Test Dependencies Missing**
   ```bash
   # Install test requirements
   pip3 install -r test_requirements.txt
   
   # Or use the simple test instead
   python3 tests/test_simple.py
   ```

4. **Tests Timing Out**
   ```bash
   # Check service logs
   make logs
   
   # Increase timeout in test scripts
   # Edit test files and increase timeout values
   ```

### Service-Specific Debugging

1. **API Backend Issues**
   ```bash
   # Check API health
   curl http://localhost:8000/docs
   
   # View logs
   docker compose logs api-backend
   ```

2. **Vector Store Issues**
   ```bash
   # Check vector store health
   curl http://localhost:8001/docs
   
   # View logs  
   docker compose logs vector-store
   ```

3. **Streamlit UI Issues**
   ```bash
   # Check UI accessibility
   curl http://localhost:8501
   
   # View logs
   docker compose logs streamlit-ui
   ```

## 📈 Performance Benchmarks

### Expected Performance
- Service startup: < 60 seconds
- Document upload: < 10 seconds per PDF
- Search queries: < 3 seconds
- Document listing: < 2 seconds
- Document deletion: < 5 seconds

### Resource Usage
- Memory: ~1-2 GB total for all services
- CPU: Moderate during document processing
- Disk: ~100 MB for service images + document storage

## 🔄 Continuous Testing

### Automated Testing Setup
```bash
# Add to CI/CD pipeline
#!/bin/bash
cd /path/to/project
python3 tests/test_simple.py
if [ $? -eq 0 ]; then
    echo "✅ Tests passed"
else
    echo "❌ Tests failed"
    exit 1
fi
```

### Regular Health Checks
```bash
# Cron job for regular verification
0 */6 * * * cd /path/to/project && make verify
```

## 📝 Test Reports

Test results are saved in JSON format:
- `test_results.json` - Simple test results
- `test_results_advanced.json` - Advanced test results

Example test result structure:
```json
{
  "startup": true,
  "services_healthy": true,
  "document_uploads": {
    "total": 2,
    "successful": 2,
    "success_rate": 1.0
  },
  "search_tests": {
    "total": 4,
    "successful": 3,
    "success_rate": 0.75
  }
}
```

## 🎯 Next Steps

After running tests successfully:

1. **Development**: Services are ready for development use
2. **Production**: Consider additional security and monitoring tests
3. **Load Testing**: Test with larger document sets and concurrent users
4. **Performance Tuning**: Optimize based on test results and usage patterns

For additional help or issues, check the service logs and ensure all dependencies are correctly installed.