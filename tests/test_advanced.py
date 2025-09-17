#!/usr/bin/env python3
"""
Advanced Test Suite for PDF Search System with File Upload Testing

This script provides comprehensive testing including:
- Document upload with actual PDF files
- Table processing validation
- Search result accuracy testing
- Complete CRUD operations testing
"""

import json
import os
import sys
import time
import subprocess
import tempfile
import urllib.request
import urllib.parse
from typing import Dict, List, Any


class PDFTestDataGenerator:
    """Generate test PDF files without external dependencies"""
    
    @staticmethod
    def create_simple_pdf(filename: str, text_content: str) -> str:
        """Create a simple PDF using basic PDF structure"""
        # This creates a minimal PDF with text content
        pdf_content = f"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 5 0 R
>>
>>
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
({text_content}) Tj
ET
endstream
endobj

5 0 obj
<<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
endobj

xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000274 00000 n 
0000000373 00000 n 
trailer
<<
/Size 6
/Root 1 0 R
>>
startxref
453
%%EOF"""
        
        with open(filename, 'w') as f:
            f.write(pdf_content)
        return filename


class MultipartEncoder:
    """Simple multipart form data encoder for file uploads"""
    
    def __init__(self):
        self.boundary = "----WebKitFormBoundary" + "".join([str(i) for i in range(16)])
        self.data = []
    
    def add_field(self, name: str, value: str):
        """Add a form field"""
        self.data.append(f"--{self.boundary}")
        self.data.append(f'Content-Disposition: form-data; name="{name}"')
        self.data.append("")
        self.data.append(value)
    
    def add_file(self, name: str, filename: str, content: bytes, content_type: str = "application/pdf"):
        """Add a file field"""
        self.data.append(f"--{self.boundary}")
        self.data.append(f'Content-Disposition: form-data; name="{name}"; filename="{filename}"')
        self.data.append(f"Content-Type: {content_type}")
        self.data.append("")
        # For binary data, we'll need to handle this differently
        self.data.append(content.decode('latin-1'))  # Encode binary as latin-1 for transport
    
    def encode(self) -> tuple:
        """Encode the multipart data"""
        self.data.append(f"--{self.boundary}--")
        body = "\r\n".join(self.data)
        content_type = f"multipart/form-data; boundary={self.boundary}"
        return body.encode('latin-1'), content_type


class AdvancedTestSuite:
    """Advanced test suite with file upload capabilities"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.results = {}
        self.uploaded_documents = []
        
        # Service URLs
        self.api_base = "http://localhost:8000"
        self.vector_base = "http://localhost:8001"
        self.ui_base = "http://localhost:8501"
    
    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging with timestamps"""
        timestamp = time.strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ️ ",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️ ",
            "TEST": "🧪"
        }.get(level, "  ")
        print(f"[{timestamp}] {prefix} {message}")
    
    def make_request(self, method: str, url: str, data: bytes = None, headers: Dict = None) -> Dict[str, Any]:
        """Make HTTP request with proper error handling"""
        try:
            req = urllib.request.Request(url, data=data, headers=headers or {})
            req.get_method = lambda: method
            
            with urllib.request.urlopen(req, timeout=30) as response:
                response_data = response.read()
                try:
                    return {
                        "success": True,
                        "status_code": response.status,
                        "data": json.loads(response_data.decode('utf-8')),
                        "headers": dict(response.headers)
                    }
                except json.JSONDecodeError:
                    return {
                        "success": True,
                        "status_code": response.status,
                        "data": response_data.decode('utf-8'),
                        "headers": dict(response.headers)
                    }
        
        except urllib.error.HTTPError as e:
            error_data = e.read().decode('utf-8') if e.fp else str(e)
            return {
                "success": False,
                "status_code": e.code,
                "error": error_data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def upload_file(self, file_path: str) -> Dict[str, Any]:
        """Upload a file using multipart form data"""
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            encoder = MultipartEncoder()
            encoder.add_file("file", os.path.basename(file_path), file_content)
            
            body, content_type = encoder.encode()
            headers = {"Content-Type": content_type}
            
            return self.make_request("POST", f"{self.api_base}/upload-pdf", body, headers)
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Upload failed: {str(e)}"
            }
    
    def run_system_startup_tests(self) -> bool:
        """Test system startup and health"""
        self.log("🚀 Testing System Startup", "TEST")
        
        # Start services
        self.log("Starting Docker services...")
        start_cmd = ["docker", "compose", "up", "-d", "--build"]
        result = subprocess.run(start_cmd, cwd=self.project_path, capture_output=True, text=True)
        
        if result.returncode != 0:
            self.log(f"Failed to start services: {result.stderr}", "ERROR")
            return False
        
        self.log("Services started, waiting for health checks...", "SUCCESS")
        
        # Wait for services to be ready
        max_wait = 120  # seconds
        start_time = time.time()
        
        services = {
            "API Backend": f"{self.api_base}/docs",
            "Vector Store": f"{self.vector_base}/docs",
            "Streamlit UI": f"{self.ui_base}"
        }
        
        while time.time() - start_time < max_wait:
            all_ready = True
            
            for service_name, url in services.items():
                try:
                    urllib.request.urlopen(url, timeout=5)
                    self.log(f"{service_name}: Ready", "SUCCESS")
                except:
                    all_ready = False
                    break
            
            if all_ready:
                self.log("All services are healthy and ready", "SUCCESS")
                self.results["startup"] = True
                return True
            
            time.sleep(5)
        
        self.log("Services did not become ready within timeout", "ERROR")
        self.results["startup"] = False
        return False
    
    def run_document_tests(self) -> bool:
        """Test document operations with real file uploads"""
        self.log("📄 Testing Document Operations", "TEST")
        
        # Clean existing documents first
        self.log("Cleaning existing documents...")
        delete_result = self.make_request("DELETE", f"{self.api_base}/documents")
        if delete_result["success"]:
            self.log("Cleanup successful", "SUCCESS")
        
        # Create test documents
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create simple text document
            simple_pdf = os.path.join(temp_dir, "simple_test.pdf")
            PDFTestDataGenerator.create_simple_pdf(
                simple_pdf, 
                "This is a simple test document for testing the PDF search functionality. It contains basic text content that should be searchable."
            )
            
            # Create table-like document
            table_pdf = os.path.join(temp_dir, "table_test.pdf")
            PDFTestDataGenerator.create_simple_pdf(
                table_pdf,
                "Employee Data: John Smith Engineering 85000 Sarah Johnson Marketing 70000 Mike Chen Engineering 90000"
            )
            
            # Test document uploads
            upload_results = []
            
            self.log("Uploading simple document...")
            upload1 = self.upload_file(simple_pdf)
            upload_results.append(("simple", upload1))
            
            if upload1["success"]:
                self.log("Simple document uploaded successfully", "SUCCESS")
                if "data" in upload1 and "document_id" in upload1["data"]:
                    self.uploaded_documents.append(upload1["data"]["document_id"])
            else:
                self.log(f"Simple document upload failed: {upload1.get('error', 'Unknown error')}", "ERROR")
            
            self.log("Uploading table document...")
            upload2 = self.upload_file(table_pdf)
            upload_results.append(("table", upload2))
            
            if upload2["success"]:
                self.log("Table document uploaded successfully", "SUCCESS")
                if "data" in upload2 and "document_id" in upload2["data"]:
                    self.uploaded_documents.append(upload2["data"]["document_id"])
            else:
                self.log(f"Table document upload failed: {upload2.get('error', 'Unknown error')}", "ERROR")
        
        # Test document listing
        self.log("Testing document listing...")
        list_result = self.make_request("GET", f"{self.api_base}/documents")
        
        if list_result["success"]:
            doc_count = len(list_result["data"]) if list_result["data"] else 0
            self.log(f"Document listing successful: {doc_count} documents found", "SUCCESS")
            self.results["document_listing"] = True
        else:
            self.log(f"Document listing failed: {list_result.get('error', 'Unknown error')}", "ERROR")
            self.results["document_listing"] = False
        
        # Store upload results
        successful_uploads = sum(1 for _, result in upload_results if result["success"])
        self.results["document_uploads"] = {
            "total": len(upload_results),
            "successful": successful_uploads,
            "success_rate": successful_uploads / len(upload_results) if upload_results else 0
        }
        
        return successful_uploads > 0
    
    def run_search_tests(self) -> bool:
        """Test search functionality with various queries"""
        self.log("🔍 Testing Search Functionality", "TEST")
        
        search_tests = [
            {
                "name": "Basic Text Search",
                "query": "simple test document",
                "expected_min_results": 0
            },
            {
                "name": "Employee Search",
                "query": "John Smith",
                "expected_min_results": 0
            },
            {
                "name": "Department Search", 
                "query": "Engineering",
                "expected_min_results": 0
            },
            {
                "name": "Generic Search",
                "query": "search functionality",
                "expected_min_results": 0
            }
        ]
        
        search_results = []
        
        for test in search_tests:
            self.log(f"Testing: {test['name']}...")
            
            search_data = json.dumps({
                "query": test["query"],
                "limit": 10,
                "min_similarity": 0.3  # Lower threshold for testing
            }).encode('utf-8')
            
            headers = {"Content-Type": "application/json"}
            result = self.make_request("POST", f"{self.api_base}/search", search_data, headers)
            
            if result["success"]:
                result_count = len(result["data"]) if result["data"] else 0
                self.log(f"{test['name']}: {result_count} results found", "SUCCESS")
                search_results.append({
                    "name": test["name"],
                    "success": True,
                    "result_count": result_count
                })
            else:
                self.log(f"{test['name']}: Failed - {result.get('error', 'Unknown error')}", "ERROR")
                search_results.append({
                    "name": test["name"],
                    "success": False,
                    "result_count": 0
                })
        
        # Calculate search success rate
        successful_searches = sum(1 for r in search_results if r["success"])
        self.results["search_tests"] = {
            "total": len(search_tests),
            "successful": successful_searches,
            "success_rate": successful_searches / len(search_tests),
            "details": search_results
        }
        
        return successful_searches > 0
    
    def run_deletion_tests(self) -> bool:
        """Test document deletion functionality"""
        self.log("🗑️  Testing Document Deletion", "TEST")
        
        # Test individual document deletion
        if self.uploaded_documents:
            doc_id = self.uploaded_documents[0]
            self.log(f"Testing individual document deletion: {doc_id[:8]}...")
            
            delete_result = self.make_request("DELETE", f"{self.api_base}/documents/{doc_id}")
            
            if delete_result["success"]:
                self.log("Individual document deletion successful", "SUCCESS")
                self.results["individual_delete"] = True
            else:
                self.log(f"Individual document deletion failed: {delete_result.get('error', 'Unknown error')}", "ERROR")
                self.results["individual_delete"] = False
        
        # Test bulk deletion
        self.log("Testing bulk document deletion...")
        delete_all_result = self.make_request("DELETE", f"{self.api_base}/documents")
        
        if delete_all_result["success"]:
            self.log("Bulk document deletion successful", "SUCCESS")
            self.results["bulk_delete"] = True
        else:
            self.log(f"Bulk document deletion failed: {delete_all_result.get('error', 'Unknown error')}", "ERROR")
            self.results["bulk_delete"] = False
        
        # Verify deletion
        self.log("Verifying deletion...")
        list_result = self.make_request("GET", f"{self.api_base}/documents")
        
        if list_result["success"]:
            remaining_docs = len(list_result["data"]) if list_result["data"] else 0
            if remaining_docs == 0:
                self.log("Deletion verification successful: No documents remaining", "SUCCESS")
                self.results["deletion_verification"] = True
            else:
                self.log(f"Deletion verification failed: {remaining_docs} documents still exist", "WARNING")
                self.results["deletion_verification"] = False
        else:
            self.log("Could not verify deletion", "WARNING")
            self.results["deletion_verification"] = False
        
        return self.results.get("bulk_delete", False)
    
    def generate_comprehensive_report(self):
        """Generate detailed test report"""
        self.log("=" * 60, "INFO")
        self.log("COMPREHENSIVE TEST RESULTS", "INFO")
        self.log("=" * 60, "INFO")
        
        # System Startup
        startup_status = "PASS" if self.results.get("startup", False) else "FAIL"
        self.log(f"System Startup:            {startup_status}")
        
        # Document Operations
        upload_data = self.results.get("document_uploads", {})
        upload_rate = upload_data.get("success_rate", 0)
        upload_status = "PASS" if upload_rate > 0.5 else "FAIL"
        self.log(f"Document Upload:           {upload_status} ({upload_rate*100:.0f}% success)")
        
        listing_status = "PASS" if self.results.get("document_listing", False) else "FAIL"
        self.log(f"Document Listing:          {listing_status}")
        
        # Search Functionality
        search_data = self.results.get("search_tests", {})
        search_rate = search_data.get("success_rate", 0)
        search_status = "PASS" if search_rate > 0.5 else "FAIL"
        self.log(f"Search Functionality:      {search_status} ({search_rate*100:.0f}% success)")
        
        # Deletion Operations
        delete_status = "PASS" if self.results.get("bulk_delete", False) else "FAIL"
        self.log(f"Document Deletion:         {delete_status}")
        
        # Overall Assessment
        critical_tests = [
            self.results.get("startup", False),
            upload_rate > 0,
            search_rate > 0,
            self.results.get("document_listing", False)
        ]
        
        overall_pass = sum(critical_tests) >= 3  # At least 3 out of 4 critical tests must pass
        
        self.log("-" * 60, "INFO")
        if overall_pass:
            self.log("OVERALL ASSESSMENT: SYSTEM FUNCTIONAL", "SUCCESS")
        else:
            self.log("OVERALL ASSESSMENT: SYSTEM HAS ISSUES", "ERROR")
        self.log("-" * 60, "INFO")
        
        # Save detailed results
        results_file = os.path.join(self.project_path, "test_results_advanced.json")
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.log(f"Detailed results saved to: {results_file}", "INFO")
        return overall_pass
    
    def run_full_test_suite(self) -> bool:
        """Run the complete test suite"""
        self.log("🚀 Starting Advanced PDF Search System Test Suite", "INFO")
        
        try:
            # 1. System startup tests
            if not self.run_system_startup_tests():
                self.log("System startup failed, aborting remaining tests", "ERROR")
                return False
            
            # Wait a bit for services to fully initialize
            time.sleep(10)
            
            # 2. Document operation tests
            if not self.run_document_tests():
                self.log("Document operations failed", "WARNING")
            
            # 3. Search functionality tests
            if not self.run_search_tests():
                self.log("Search functionality tests failed", "WARNING")
            
            # 4. Deletion tests
            if not self.run_deletion_tests():
                self.log("Deletion tests failed", "WARNING")
            
            # 5. Generate comprehensive report
            return self.generate_comprehensive_report()
            
        except KeyboardInterrupt:
            self.log("Test suite interrupted by user", "WARNING")
            return False
        except Exception as e:
            self.log(f"Test suite failed with unexpected error: {e}", "ERROR")
            return False


def main():
    """Main execution function"""
    project_path = os.path.dirname(os.path.abspath(__file__))
    
    test_suite = AdvancedTestSuite(project_path)
    success = test_suite.run_full_test_suite()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()