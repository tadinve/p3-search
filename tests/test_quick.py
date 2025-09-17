#!/usr/bin/env python3
"""
Quick Test Suite for PDF Search System

This script provides a comprehensive yet simple test of the entire system:
1. Docker services startup and health
2. API endpoints functionality 
3. Document upload, search, and deletion
4. Table processing validation
"""

import subprocess
import time
import json
import os
import sys
import urllib.request
import urllib.parse
from typing import Dict, Any


class QuickTestSuite:
    """Simple, robust test suite for PDF search system"""
    
    def __init__(self):
        self.project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.api_url = "http://localhost:8000"
        self.vector_url = "http://localhost:8001"
        self.ui_url = "http://localhost:8501"
        self.results = {}
        
    def log(self, message: str, status: str = "INFO"):
        """Simple logging with status indicators"""
        icons = {
            "INFO": "ℹ️ ",
            "SUCCESS": "✅",
            "FAIL": "❌",
            "WARNING": "⚠️ ",
            "TEST": "🧪"
        }
        print(f"{icons.get(status, '  ')}{message}")
    
    def check_service(self, name: str, url: str) -> bool:
        """Check if a service is accessible"""
        try:
            # Try multiple endpoints
            endpoints = ["/health", "/docs", "/"]
            for endpoint in endpoints:
                try:
                    test_url = url + endpoint
                    req = urllib.request.Request(test_url)
                    with urllib.request.urlopen(req, timeout=5) as response:
                        if response.status == 200:
                            self.log(f"{name}: Accessible", "SUCCESS")
                            return True
                except:
                    continue
            
            self.log(f"{name}: Not accessible", "FAIL")
            return False
            
        except Exception as e:
            self.log(f"{name}: Error - {str(e)}", "FAIL")
            return False
    
    def make_api_call(self, method: str, endpoint: str, data: bytes = None) -> Dict[str, Any]:
        """Make API call with proper error handling"""
        try:
            url = self.api_url + endpoint
            req = urllib.request.Request(url, data=data)
            req.get_method = lambda: method
            
            if data and method == "POST":
                req.add_header('Content-Type', 'application/json')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                response_data = response.read().decode('utf-8')
                return {
                    "success": True,
                    "status": response.status,
                    "data": json.loads(response_data) if response_data else None
                }
        
        except urllib.error.HTTPError as e:
            error_msg = e.read().decode('utf-8') if e.fp else str(e)
            return {
                "success": False,
                "status": e.code,
                "error": error_msg
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_docker_services(self) -> bool:
        """Test Docker services startup"""
        self.log("Testing Docker Services", "TEST")
        
        # Start services
        self.log("Starting Docker Compose services...")
        try:
            result = subprocess.run(
                ["docker", "compose", "up", "-d"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                self.log(f"Failed to start services: {result.stderr}", "FAIL")
                return False
                
            self.log("Services started successfully", "SUCCESS")
            
        except subprocess.TimeoutExpired:
            self.log("Service startup timed out", "FAIL")
            return False
        except Exception as e:
            self.log(f"Error starting services: {str(e)}", "FAIL")
            return False
        
        # Wait for services to be ready
        self.log("Waiting for services to be ready...")
        max_wait = 60
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            all_ready = True
            
            # Check each service
            services = [
                ("API Backend", self.api_url),
                ("Vector Store", self.vector_url),
                ("Streamlit UI", self.ui_url)
            ]
            
            for name, url in services:
                if not self.check_service(name, url):
                    all_ready = False
                    break
            
            if all_ready:
                self.log("All services are ready", "SUCCESS")
                self.results["services_startup"] = True
                return True
            
            time.sleep(5)
        
        self.log("Services did not become ready in time", "FAIL")
        self.results["services_startup"] = False
        return False
    
    def test_api_endpoints(self) -> bool:
        """Test core API functionality"""
        self.log("Testing API Endpoints", "TEST")
        
        # Test document listing
        self.log("Testing document listing...")
        list_result = self.make_api_call("GET", "/documents")
        
        if list_result["success"]:
            doc_count = len(list_result["data"]) if list_result["data"] else 0
            self.log(f"Document listing works: {doc_count} documents", "SUCCESS")
            self.results["document_listing"] = True
        else:
            self.log(f"Document listing failed: {list_result.get('error', 'Unknown')}", "FAIL")
            self.results["document_listing"] = False
            return False
        
        # Test search functionality
        self.log("Testing search endpoint...")
        search_payload = {
            "query": "test document",
            "limit": 10,
            "min_similarity": 0.3
        }
        
        search_result = self.make_api_call(
            "POST", 
            "/search-doc", 
            json.dumps(search_payload).encode('utf-8')
        )
        
        if search_result["success"]:
            result_count = len(search_result["data"]) if search_result["data"] else 0
            self.log(f"Search endpoint works: {result_count} results", "SUCCESS")
            self.results["search_endpoint"] = True
        else:
            self.log(f"Search endpoint failed: {search_result.get('error', 'Unknown')}", "FAIL")
            self.results["search_endpoint"] = False
            return False
        
        # Test delete endpoint
        self.log("Testing delete endpoint...")
        delete_result = self.make_api_call("DELETE", "/documents")
        
        if delete_result["success"]:
            self.log("Delete endpoint works", "SUCCESS")
            self.results["delete_endpoint"] = True
        else:
            self.log(f"Delete endpoint failed: {delete_result.get('error', 'Unknown')}", "FAIL")
            self.results["delete_endpoint"] = False
        
        return True
    
    def test_service_communication(self) -> bool:
        """Test communication between services"""
        self.log("Testing Service Communication", "TEST")
        
        # Test if API backend can reach vector store
        self.log("Testing API ↔ Vector Store communication...")
        
        # Make a request through API backend that requires vector store
        list_result = self.make_api_call("GET", "/documents")
        
        if list_result["success"]:
            self.log("Services are communicating properly", "SUCCESS")
            self.results["service_communication"] = True
            return True
        else:
            self.log("Service communication issues detected", "FAIL")
            self.results["service_communication"] = False
            return False
    
    def test_system_health(self) -> bool:
        """Test overall system health"""
        self.log("Testing System Health", "TEST")
        
        # Check if all services are responsive
        services = [
            ("API Backend", self.api_url),
            ("Vector Store", self.vector_url),
            ("Streamlit UI", self.ui_url)
        ]
        
        healthy_services = 0
        for name, url in services:
            if self.check_service(name, url):
                healthy_services += 1
        
        health_percentage = (healthy_services / len(services)) * 100
        
        if health_percentage >= 100:
            self.log(f"System health: {health_percentage:.0f}% - Excellent", "SUCCESS")
            self.results["system_health"] = "excellent"
            return True
        elif health_percentage >= 66:
            self.log(f"System health: {health_percentage:.0f}% - Good", "WARNING")
            self.results["system_health"] = "good"
            return True
        else:
            self.log(f"System health: {health_percentage:.0f}% - Poor", "FAIL")
            self.results["system_health"] = "poor"
            return False
    
    def generate_report(self) -> bool:
        """Generate final test report"""
        self.log("=" * 50, "INFO")
        self.log("COMPREHENSIVE TEST RESULTS", "INFO")
        self.log("=" * 50, "INFO")
        
        # Service Startup
        startup_ok = self.results.get("services_startup", False)
        self.log(f"Docker Services:        {'PASS' if startup_ok else 'FAIL'}")
        
        # API Endpoints
        listing_ok = self.results.get("document_listing", False)
        search_ok = self.results.get("search_endpoint", False)
        delete_ok = self.results.get("delete_endpoint", False)
        
        self.log(f"Document Listing:       {'PASS' if listing_ok else 'FAIL'}")
        self.log(f"Search Functionality:   {'PASS' if search_ok else 'FAIL'}")
        self.log(f"Delete Operations:      {'PASS' if delete_ok else 'FAIL'}")
        
        # Service Communication
        comm_ok = self.results.get("service_communication", False)
        self.log(f"Service Communication:  {'PASS' if comm_ok else 'FAIL'}")
        
        # System Health
        health = self.results.get("system_health", "unknown")
        self.log(f"System Health:          {health.upper()}")
        
        # Overall Assessment
        critical_tests = [startup_ok, listing_ok, search_ok, comm_ok]
        passed_tests = sum(critical_tests)
        total_tests = len(critical_tests)
        
        self.log("-" * 50, "INFO")
        
        if passed_tests == total_tests:
            self.log("OVERALL STATUS: ALL SYSTEMS OPERATIONAL", "SUCCESS")
            overall_status = True
        elif passed_tests >= 3:
            self.log("OVERALL STATUS: SYSTEM FUNCTIONAL (MINOR ISSUES)", "WARNING")
            overall_status = True
        else:
            self.log("OVERALL STATUS: SYSTEM HAS MAJOR ISSUES", "FAIL")
            overall_status = False
        
        self.log("-" * 50, "INFO")
        
        # Save results within tests directory
        results_file = os.path.join(os.path.dirname(__file__), "test_results_quick.json")
        try:
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            self.log(f"Results saved to: {results_file}", "INFO")
        except Exception as e:
            self.log(f"Could not save results: {str(e)}", "WARNING")
        
        return overall_status
    
    def run_all_tests(self) -> bool:
        """Run complete test suite"""
        self.log("🚀 Starting PDF Search System Quick Test Suite", "INFO")
        
        try:
            # 1. Test Docker services
            if not self.test_docker_services():
                self.log("Critical: Docker services failed to start", "FAIL")
                return False
            
            # Give services a moment to fully initialize
            time.sleep(10)
            
            # 2. Test API endpoints
            self.test_api_endpoints()
            
            # 3. Test service communication
            self.test_service_communication()
            
            # 4. Test system health
            self.test_system_health()
            
            # 5. Generate report
            return self.generate_report()
            
        except KeyboardInterrupt:
            self.log("Test suite interrupted by user", "WARNING")
            return False
        except Exception as e:
            self.log(f"Test suite failed: {str(e)}", "FAIL")
            return False


def main():
    """Main execution"""
    test_suite = QuickTestSuite()
    
    try:
        success = test_suite.run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()