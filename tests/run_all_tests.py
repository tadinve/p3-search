#!/usr/bin/env python3
"""
Unified Test Runner for PDF Search System
=========================================

This script runs all available tests in sequence without requiring user input.
Similar to pytest, it provides a single command to execute the entire test suite.

Usage:
    python run_all_tests.py
    
Or via make:
    make test-all
"""

import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

class TestRunner:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_results": []
        }
        self.tests_dir = Path(__file__).parent
        
    def print_header(self):
        """Print the test suite header"""
        print("=" * 80)
        print("🚀 PDF SEARCH SYSTEM - UNIFIED TEST SUITE")
        print("=" * 80)
        print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📂 Working directory: {self.tests_dir}")
        print("=" * 80)
        
    def run_test(self, test_name, test_file):
        """Run a single test and capture results"""
        print(f"\n🧪 Running {test_name}...")
        print("-" * 60)
        
        start_time = time.time()
        try:
            # Run the test
            result = subprocess.run(
                [sys.executable, test_file],
                cwd=self.tests_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            duration = time.time() - start_time
            
            # Determine if test passed based on return code and output
            success = result.returncode == 0
            
            test_result = {
                "test_name": test_name,
                "test_file": test_file,
                "success": success,
                "duration": round(duration, 2),
                "return_code": result.returncode,
                "stdout_lines": len(result.stdout.splitlines()) if result.stdout else 0,
                "stderr_lines": len(result.stderr.splitlines()) if result.stderr else 0
            }
            
            # Print test output
            if result.stdout:
                print(result.stdout)
            
            if result.stderr and not success:
                print("❌ STDERR:")
                print(result.stderr)
            
            # Print result summary
            if success:
                print(f"✅ {test_name} PASSED ({duration:.2f}s)")
                self.results["passed_tests"] += 1
            else:
                print(f"❌ {test_name} FAILED ({duration:.2f}s)")
                self.results["failed_tests"] += 1
                
            self.results["test_results"].append(test_result)
            self.results["total_tests"] += 1
            
            return success
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_name} TIMEOUT (exceeded 5 minutes)")
            test_result = {
                "test_name": test_name,
                "test_file": test_file,
                "success": False,
                "duration": 300,
                "return_code": -1,
                "error": "Timeout"
            }
            self.results["test_results"].append(test_result)
            self.results["failed_tests"] += 1
            self.results["total_tests"] += 1
            return False
            
        except Exception as e:
            print(f"💥 {test_name} ERROR: {str(e)}")
            test_result = {
                "test_name": test_name,
                "test_file": test_file,
                "success": False,
                "duration": time.time() - start_time,
                "return_code": -1,
                "error": str(e)
            }
            self.results["test_results"].append(test_result)
            self.results["failed_tests"] += 1
            self.results["total_tests"] += 1
            return False
    
    def print_summary(self):
        """Print final test summary"""
        print("\n" + "=" * 80)
        print("📊 TEST SUITE SUMMARY")
        print("=" * 80)
        
        total = self.results["total_tests"]
        passed = self.results["passed_tests"]
        failed = self.results["failed_tests"]
        
        print(f"📈 Total Tests:   {total}")
        print(f"✅ Passed:        {passed}")
        print(f"❌ Failed:        {failed}")
        print(f"📊 Success Rate:  {(passed/total*100):.1f}%" if total > 0 else "📊 Success Rate:  0%")
        
        print("\n📋 Individual Test Results:")
        print("-" * 80)
        
        for test in self.results["test_results"]:
            status = "✅ PASS" if test["success"] else "❌ FAIL"
            duration = test["duration"]
            print(f"{status} {test['test_name']:<25} ({duration:>6.2f}s)")
        
        print("-" * 80)
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED! System is fully operational.")
            return_code = 0
        else:
            print(f"⚠️  {failed} test(s) failed. Please review the output above.")
            return_code = 1
            
        # Save detailed results
        results_file = self.tests_dir / "unified_test_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"💾 Detailed results saved to: {results_file}")
        print("=" * 80)
        
        return return_code
    
    def run_all_tests(self):
        """Run all available tests"""
        self.print_header()
        
        # Define test suite in order of execution
        test_suite = [
            ("Quick Comprehensive Test", "test_quick.py"),
            ("Simple Validation Test", "test_simple.py"),
            ("Advanced Performance Test", "test_advanced.py"),
            ("System Integration Test", "test_system.py"),
            ("Comprehensive Professional Test", "test_comprehensive.py"),
            ("Table PDF Processing Test", "test_table_pdf.py"),
            ("Table Simple Functionality Test", "test_table_simple.py"),
            ("Table Validation Test", "test_table_validation.py")
        ]
        
        # Run each test
        for test_name, test_file in test_suite:
            test_path = self.tests_dir / test_file
            if test_path.exists():
                self.run_test(test_name, test_file)
            else:
                print(f"⚠️  Skipping {test_name}: {test_file} not found")
        
        # Print final summary and return appropriate exit code
        return self.print_summary()

def main():
    """Main entry point"""
    runner = TestRunner()
    exit_code = runner.run_all_tests()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()