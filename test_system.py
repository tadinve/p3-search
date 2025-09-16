#!/usr/bin/env python3
"""
Test script for the PDF Document Search System
Run this after starting both services to verify functionality.
"""

import requests
import time
import json
from pathlib import Path

# Service URLs
API_BASE_URL = "http://localhost:8000"
VECTOR_STORE_URL = "http://localhost:8001"

def check_services():
    """Check if both services are running"""
    print("🔍 Checking service health...")
    
    try:
        # Check API backend
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Backend is healthy")
        else:
            print("❌ API Backend is not responding correctly")
            return False
    except requests.exceptions.RequestException:
        print("❌ API Backend is not accessible")
        return False
    
    try:
        # Check vector store
        response = requests.get(f"{VECTOR_STORE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Vector Store is healthy")
        else:
            print("❌ Vector Store is not responding correctly")
            return False
    except requests.exceptions.RequestException:
        print("❌ Vector Store is not accessible")
        return False
    
    return True

def test_api_info():
    """Test API info endpoint"""
    print("\n📋 Testing API info...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            print("✅ API info endpoint working")
            data = response.json()
            print(f"   Service: {data.get('message')}")
            print(f"   Version: {data.get('version')}")
        else:
            print("❌ API info endpoint failed")
    except Exception as e:
        print(f"❌ Error testing API info: {e}")

def create_sample_pdf():
    """Create a sample PDF for testing (requires reportlab)"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        filename = "test_document.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        
        # Add some sample content
        c.drawString(100, 750, "Sample Document for Testing")
        c.drawString(100, 720, "This document contains information about machine learning.")
        c.drawString(100, 690, "Artificial intelligence is transforming industries.")
        c.drawString(100, 660, "Deep learning models require large datasets.")
        c.drawString(100, 630, "Neural networks can process complex patterns.")
        c.drawString(100, 600, "Natural language processing enables text analysis.")
        c.drawString(100, 570, "Computer vision algorithms can recognize objects.")
        c.drawString(100, 540, "Data science combines statistics and programming.")
        
        c.save()
        print(f"✅ Created sample PDF: {filename}")
        return filename
    except ImportError:
        print("⚠️  reportlab not installed. Please create a test PDF manually.")
        return None

def test_upload_and_search():
    """Test the main functionality"""
    print("\n🧪 Testing upload and search functionality...")
    
    # Check for existing PDF files
    pdf_files = list(Path(".").glob("*.pdf"))
    
    if not pdf_files:
        print("📄 No PDF files found. Creating a sample...")
        sample_pdf = create_sample_pdf()
        if not sample_pdf:
            print("⚠️  Please place a PDF file in the current directory and run the test again.")
            return
        pdf_file = sample_pdf
    else:
        pdf_file = str(pdf_files[0])
        print(f"📄 Using PDF file: {pdf_file}")
    
    # Test upload
    print("\n📤 Testing PDF upload...")
    try:
        with open(pdf_file, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{API_BASE_URL}/upload-pdf", files=files)
            
        if response.status_code == 200:
            upload_result = response.json()
            document_id = upload_result['document_id']
            print("✅ PDF uploaded successfully")
            print(f"   Document ID: {document_id}")
            print(f"   Lines processed: {upload_result['lines_processed']}")
        else:
            print(f"❌ Upload failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error during upload: {e}")
        return
    
    # Wait a moment for processing
    print("\n⏳ Waiting for processing...")
    time.sleep(2)
    
    # Test search
    print("\n🔍 Testing document search...")
    search_queries = [
        "machine learning",
        "artificial intelligence", 
        "data science",
        "neural networks"
    ]
    
    for query in search_queries:
        try:
            search_data = {"query": query, "limit": 3}
            response = requests.post(f"{API_BASE_URL}/search-doc", json=search_data)
            
            if response.status_code == 200:
                results = response.json()
                print(f"\n🔎 Search results for '{query}':")
                if results:
                    for i, result in enumerate(results, 1):
                        print(f"   {i}. Document: {result['filename']}")
                        print(f"      Line {result['line_number']}: {result['content'][:100]}...")
                        print(f"      Similarity: {result['similarity_score']:.3f}")
                else:
                    print("   No results found")
            else:
                print(f"❌ Search failed for '{query}': {response.text}")
        except Exception as e:
            print(f"❌ Error during search for '{query}': {e}")
    
    # Test document retrieval
    print(f"\n📖 Testing document retrieval for ID: {document_id}")
    try:
        response = requests.get(f"{API_BASE_URL}/documents/{document_id}")
        if response.status_code == 200:
            doc_data = response.json()
            print("✅ Document retrieved successfully")
            print(f"   Filename: {doc_data['filename']}")
            print(f"   Total lines: {len(doc_data['lines'])}")
        else:
            print(f"❌ Document retrieval failed: {response.text}")
    except Exception as e:
        print(f"❌ Error during document retrieval: {e}")

def main():
    """Main test function"""
    print("🚀 PDF Document Search System - Test Suite")
    print("=" * 50)
    
    # Check if services are running
    if not check_services():
        print("\n❌ Services are not running. Please start them first:")
        print("   Docker: docker-compose up")
        print("   Manual: Follow README instructions")
        return
    
    # Test API info
    test_api_info()
    
    # Test main functionality
    test_upload_and_search()
    
    print("\n🎉 Test completed!")
    print("\n💡 Next steps:")
    print("   - Try uploading your own PDF files")
    print("   - Experiment with different search queries")
    print("   - Check the API documentation at http://localhost:8000/docs")

if __name__ == "__main__":
    main()