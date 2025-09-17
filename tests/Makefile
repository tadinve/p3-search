# PDF Search System - Test Makefile

.PHONY: help test test-quick test-simple test-all test-full clean start stop status logs

# Default target
help:
	@echo "PDF Search System Test Commands (run from tests/ directory):"
	@echo ""
	@echo "Testing Commands:"
	@echo "  make test         - Run quick test suite (recommended)"
	@echo "  make test-quick   - Run quick test suite"
	@echo "  make test-simple  - Run simple test suite"
	@echo "  make test-all     - Run ALL tests with unified runner (pytest-style)"
	@echo "  make test-tables  - Run table processing validation"
	@echo "  make test-table-upload - Create and upload test table document"
	@echo "  make test-full    - Run comprehensive test suite (requires dependencies)"
	@echo "  make install-deps - Install test dependencies"
	@echo ""
	@echo "Docker Management:"
	@echo "  make start        - Start all services"
	@echo "  make stop         - Stop all services"
	@echo "  make restart      - Restart all services"
	@echo "  make status       - Show service status"
	@echo "  make logs         - Show service logs"
	@echo "  make clean        - Clean up containers and volumes"
	@echo ""

# Quick test suite (recommended - robust and comprehensive)
test: test-quick

test-quick:
	@echo "🚀 Running Quick Test Suite..."
	python3 test_quick.py

# Simple test suite (no external dependencies)
test-simple:
	@echo "🚀 Running Simple Test Suite..."
	python3 test_simple.py

# Table processing validation
test-tables:
	@echo "🧪 Running Table Processing Validation..."
	python3 utilities/validate_table_processing.py

test-table-upload:
	@echo "📄 Creating and uploading test table document..."
	python3 utilities/create_test_pdf.py

# Comprehensive test suite (requires dependencies)
test-full: install-deps
	@echo "🚀 Running Comprehensive Test Suite..."
	python3 test_comprehensive.py

# Run all available tests in sequence (unified test runner)
test-all:
	@echo "🎯 Running All Tests with Unified Test Runner..."
	python3 run_all_tests.py

# Install test dependencies
install-deps:
	@echo "📦 Installing test dependencies..."
	pip3 install -r test_requirements.txt

# Docker management commands
start:
	@echo "🚀 Starting all services..."
	cd .. && docker compose up -d --build

stop:
	@echo "🛑 Stopping all services..."
	cd .. && docker compose down

restart: stop start

status:
	@echo "📊 Service Status:"
	cd .. && docker compose ps

logs:
	@echo "📋 Service Logs:"
	cd .. && docker compose logs -f

clean:
	@echo "🧹 Cleaning up..."
	cd .. && docker compose down -v --remove-orphans
	cd .. && docker system prune -f

# Health check commands
check-api:
	@echo "🏥 Checking API Backend..."
	curl -f http://localhost:8000/docs || echo "API Backend not accessible"

check-vector:
	@echo "🏥 Checking Vector Store..."
	curl -f http://localhost:8001/docs || echo "Vector Store not accessible"

check-ui:
	@echo "🏥 Checking Streamlit UI..."
	curl -f http://localhost:8501 || echo "Streamlit UI not accessible"

check-all: check-api check-vector check-ui

# Development helpers
dev-setup: install-deps start
	@echo "✅ Development environment ready!"
	@echo "   - API Backend: http://localhost:8000"
	@echo "   - Vector Store: http://localhost:8001"
	@echo "   - Streamlit UI: http://localhost:8501"

# Test data creation
create-test-data:
	@echo "📄 Creating test PDF documents..."
	python3 -c "
	import os
	from reportlab.lib.pagesizes import letter
	from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
	from reportlab.lib.styles import getSampleStyleSheet
	from reportlab.lib import colors
	
	# Simple document
	doc = SimpleDocTemplate('test_simple.pdf', pagesize=letter)
	styles = getSampleStyleSheet()
	content = [Paragraph('This is a simple test document for PDF search functionality.', styles['Normal'])]
	doc.build(content)
	
	# Table document
	doc2 = SimpleDocTemplate('test_table.pdf', pagesize=letter)
	table_data = [['Name', 'Department', 'Salary'], ['John Smith', 'Engineering', '85000'], ['Jane Doe', 'Marketing', '70000']]
	table = Table(table_data)
	table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey), ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
	doc2.build([table])
	
	print('✅ Test PDF documents created: test_simple.pdf, test_table.pdf')
	" 2>/dev/null || echo "⚠️  reportlab not installed, skipping test data creation"

# Quick verification
verify:
	@echo "🔍 Quick system verification..."
	@make status
	@echo ""
	@make check-all
	@echo ""
	@echo "🧪 Running quick test..."
	@python3 -c "
	import urllib.request
	import json
	try:
	    # Test API health
	    urllib.request.urlopen('http://localhost:8000/docs', timeout=5)
	    print('✅ API Backend: OK')
	    
	    # Test document listing
	    req = urllib.request.Request('http://localhost:8000/documents')
	    with urllib.request.urlopen(req, timeout=5) as response:
	        data = json.loads(response.read())
	        print(f'✅ Document API: OK ({len(data)} documents)')
	    
	    print('🎉 System verification passed!')
	except Exception as e:
	    print(f'❌ System verification failed: {e}')
	"