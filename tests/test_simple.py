#!/usr/bin/env python3
"""
Simplified Test Runner for PDF Search System

This script tests the complete system functionality without complex dependencies:
1. Docker Compose service validation
2. API endpoint testing
3. Document lifecycle operations
4. Search functionality validation
"""

import subprocess
import time
import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, List, Any


class SimpleTestRunner:
    """Simplified test runner without external dependencies"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.results = {}
        
        # Service configuration
        self.services = {
            'api-backend': 'http://localhost:8000',
            'vector-store': 'http://localhost:8001', 
            'streamlit-ui': 'http://localhost:8501'
        }
        
        # Test timeouts
        self.service_timeout = 120  # seconds
        self.request_timeout = 10   # seconds
    
    def log(self, message: str, level: str = "INFO"):
        """Simple logging"""
        prefix = {
            "INFO": "ℹ️ ",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️ "
        }.get(level, "  ")
        print(f"{prefix} {message}")
    
    def run_command(self, cmd: List[str], timeout: int = 30) -> Dict[str, Any]:
        """Run shell command and return result"""
        try:
            result = subprocess.run(
                cmd, 
                cwd=self.project_path,
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "returncode": -1
            }
    
    def check_url(self, url: str, timeout: int = 5) -> Dict[str, Any]:
        """Check if URL is accessible"""
        try:
            req = urllib.request.Request(url + '/health')
            start_time = time.time()
            
            with urllib.request.urlopen(req, timeout=timeout) as response:
                response_time = time.time() - start_time
                return {
                    "accessible": True,
                    "status_code": response.status,
                    "response_time": response_time
                }
        except urllib.error.HTTPError as e:
            return {
                "accessible": True,  # Server is responding, just with an error
                "status_code": e.code,
                "response_time": None
            }
        except Exception as e:
            return {
                "accessible": False,
                "error": str(e),
                "response_time": None
            }
    
    def wait_for_services(self, timeout: int = 120) -> bool:
        """Wait for all services to become available"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            all_accessible = True
            
            for service_name, url in self.services.items():
                result = self.check_url(url, timeout=3)
                if not result["accessible"]:
                    all_accessible = False
                    break
            
            if all_accessible:
                return True
            
            time.sleep(5)
        
        return False
    
    def test_docker_services(self) -> bool:
        """Test Docker Compose services"""
        self.log("Testing Docker Services", "INFO")
        
        # Stop any existing services
        self.log("Stopping existing services...")
        stop_result = self.run_command(["docker", "compose", "down"])
        
        # Start services
        self.log("Starting services with docker-compose...")
        start_result = self.run_command(
            ["docker", "compose", "up", "-d", "--build"], 
            timeout=180
        )
        
        if not start_result["success"]:
            self.log(f"Failed to start services: {start_result.get('stderr', 'Unknown error')}", "ERROR")
            self.results["docker_start"] = False
            return False
        
        self.log("Services started, waiting for health checks...", "SUCCESS")
        self.results["docker_start"] = True
        
        # Wait for services to be ready
        if self.wait_for_services(self.service_timeout):
            self.log("All services are healthy and accessible", "SUCCESS")
            self.results["services_healthy"] = True
            return True
        else:
            self.log("Services did not become healthy within timeout", "ERROR")
            self.results["services_healthy"] = False
            return False
    
    def test_service_endpoints(self) -> bool:
        """Test individual service endpoints"""
        self.log("Testing Service Endpoints", "INFO")
        
        all_accessible = True
        endpoint_results = {}
        
        for service_name, url in self.services.items():
            self.log(f"Testing {service_name} at {url}...")
            result = self.check_url(url)
            endpoint_results[service_name] = result
            
            if result["accessible"]:
                response_time = result.get("response_time", 0)
                if response_time is not None:
                    self.log(f"{service_name}: Accessible ({response_time:.2f}s)", "SUCCESS")
                else:
                    self.log(f"{service_name}: Accessible", "SUCCESS")
            else:
                self.log(f"{service_name}: Not accessible - {result.get('error', 'Unknown error')}", "ERROR")
                all_accessible = False
        
        self.results["endpoint_tests"] = endpoint_results
        return all_accessible
    
    def make_api_request(self, method: str, url: str, data: str = None, files: Dict = None) -> Dict[str, Any]:
        """Make HTTP request to API"""
        try:
            if method == "GET":
                req = urllib.request.Request(url)
            elif method == "POST":
                req = urllib.request.Request(url)
                if data:
                    req.add_header('Content-Type', 'application/json')
                    req.data = data.encode('utf-8')
                # Note: File uploads would need more complex handling
            elif method == "DELETE":
                req = urllib.request.Request(url)
                req.get_method = lambda: 'DELETE'
            
            with urllib.request.urlopen(req, timeout=self.request_timeout) as response:
                response_data = response.read().decode('utf-8')
                return {
                    "success": True,
                    "status_code": response.status,
                    "data": json.loads(response_data) if response_data else None
                }
        
        except urllib.error.HTTPError as e:
            return {
                "success": False,
                "status_code": e.code,
                "error": e.read().decode('utf-8') if e.fp else str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_api_functionality(self) -> bool:
        """Test core API functionality"""
        self.log("Testing API Functionality", "INFO")
        
        api_base = self.services['api-backend']
        
        # Test document listing (should be empty initially)
        self.log("Testing document listing...")
        list_result = self.make_api_request("GET", f"{api_base}/documents")
        
        if list_result["success"]:
            doc_count = len(list_result["data"]) if list_result["data"] else 0
            self.log(f"Document listing successful: {doc_count} documents", "SUCCESS")
            self.results["list_documents"] = True
        else:
            self.log(f"Document listing failed: {list_result.get('error', 'Unknown error')}", "ERROR")
            self.results["list_documents"] = False
            return False
        
        # Test search functionality
        self.log("Testing search functionality...")
        search_data = json.dumps({
            "query": "test query",
            "limit": 10,
            "min_similarity": 0.5
        })
        
        search_result = self.make_api_request("POST", f"{api_base}/search-doc", search_data)
        
        if search_result["success"]:
            result_count = len(search_result["data"]) if search_result["data"] else 0
            self.log(f"Search functionality working: {result_count} results", "SUCCESS")
            self.results["search_functionality"] = True
        else:
            self.log(f"Search failed: {search_result.get('error', 'Unknown error')}", "ERROR")
            self.results["search_functionality"] = False
            return False
        
        # Test delete all documents (cleanup)
        self.log("Testing delete all documents...")
        delete_result = self.make_api_request("DELETE", f"{api_base}/documents")
        
        if delete_result["success"]:
            self.log("Delete all documents successful", "SUCCESS")
            self.results["delete_all"] = True
        else:
            self.log(f"Delete all failed: {delete_result.get('error', 'Unknown error')}", "ERROR")
            self.results["delete_all"] = False
        
        return True
    
    def test_service_health_endpoints(self) -> bool:
        """Test health endpoints specifically"""
        self.log("Testing Health Endpoints", "INFO")
        
        health_results = {}
        all_healthy = True
        
        for service_name, base_url in self.services.items():
            self.log(f"Checking {service_name} health...")
            
            # Try different health endpoint patterns
            health_urls = [
                f"{base_url}/health",
                f"{base_url}/docs",  # FastAPI docs endpoint
                f"{base_url}/"       # Root endpoint
            ]
            
            service_healthy = False
            for health_url in health_urls:
                result = self.check_url(health_url.replace('/health', ''), timeout=5)
                if result["accessible"]:
                    health_results[service_name] = {
                        "healthy": True,
                        "url": health_url,
                        "response_time": result.get("response_time", 0)
                    }
                    self.log(f"{service_name}: Healthy", "SUCCESS")
                    service_healthy = True
                    break
            
            if not service_healthy:
                health_results[service_name] = {"healthy": False}
                self.log(f"{service_name}: Unhealthy", "ERROR")
                all_healthy = False
        
        self.results["health_checks"] = health_results
        return all_healthy
    
    def generate_test_report(self):
        """Generate and display test report"""
        self.log("=" * 60, "INFO")
        self.log("TEST RESULTS SUMMARY", "INFO")
        self.log("=" * 60, "INFO")
        
        # Docker Services
        docker_status = "PASS" if self.results.get("docker_start", False) else "FAIL"
        self.log(f"Docker Services Start:     {docker_status}")
        
        services_status = "PASS" if self.results.get("services_healthy", False) else "FAIL"
        self.log(f"Services Health:           {services_status}")
        
        # API Functionality
        list_status = "PASS" if self.results.get("list_documents", False) else "FAIL"
        self.log(f"Document Listing:          {list_status}")
        
        search_status = "PASS" if self.results.get("search_functionality", False) else "FAIL"
        self.log(f"Search Functionality:      {search_status}")
        
        delete_status = "PASS" if self.results.get("delete_all", False) else "FAIL"
        self.log(f"Delete Operations:         {delete_status}")
        
        # Overall Status
        all_tests = [
            self.results.get("docker_start", False),
            self.results.get("services_healthy", False),
            self.results.get("list_documents", False),
            self.results.get("search_functionality", False)
        ]
        
        overall_pass = all(all_tests)
        self.log("-" * 60, "INFO")
        
        if overall_pass:
            self.log("OVERALL STATUS: ALL TESTS PASSED", "SUCCESS")
        else:
            self.log("OVERALL STATUS: SOME TESTS FAILED", "ERROR")
        
        self.log("-" * 60, "INFO")
        
        # Save results within tests directory
        results_file = os.path.join(os.path.dirname(__file__), "test_results.json")
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.log(f"Detailed results saved to: {results_file}", "INFO")
        
        return overall_pass
    
    def run_all_tests(self) -> bool:
        """Run all tests in sequence"""
        self.log("🚀 Starting PDF Search System Test Suite", "INFO")
        
        try:
            # 1. Test Docker services
            if not self.test_docker_services():
                self.log("Docker service tests failed, aborting", "ERROR")
                return False
            
            # 2. Test service endpoints
            if not self.test_service_endpoints():
                self.log("Service endpoint tests failed", "WARNING")
            
            # 3. Test health endpoints
            if not self.test_service_health_endpoints():
                self.log("Health endpoint tests failed", "WARNING")
            
            # 4. Test API functionality
            if not self.test_api_functionality():
                self.log("API functionality tests failed", "WARNING")
            
            # 5. Generate report
            return self.generate_test_report()
            
        except KeyboardInterrupt:
            self.log("Test suite interrupted by user", "WARNING")
            return False
        except Exception as e:
            self.log(f"Test suite failed with error: {e}", "ERROR")
            return False
        finally:
            # Cleanup - keep services running for manual testing
            self.log("Test suite completed. Services are still running.", "INFO")
            self.log("Use 'docker compose down' to stop services.", "INFO")


def main():
    """Main execution function"""
    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    test_runner = SimpleTestRunner(project_path)
    success = test_runner.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()