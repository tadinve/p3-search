#!/usr/bin/env python3
"""
PDF Search System - One Command Test Suite
==========================================

Run all tests with a single command: python test.py

This script:
- Automatically installs missing dependencies
- Runs all test suites sequentially
- Provides a comprehensive summary
- Saves detailed results
- Works out of the box with zero configuration

Usage:
    cd tests/
    python test.py

That's it! No make, no setup, just one command.
"""

import sys
import subprocess
import json
import time
import os
from datetime import datetime
from pathlib import Path

class OneCommandTestSuite:
    def __init__(self):
        # Create results directory structure
        self.tests_dir = Path(__file__).parent
        self.results_base_dir = self.tests_dir / "results"
        
        # Create timestamp-based run directory
        run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = self.results_base_dir / f"run_{run_timestamp}"
        
        # Create directories
        self.results_base_dir.mkdir(exist_ok=True)
        self.run_dir.mkdir(exist_ok=True)
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "run_id": f"run_{run_timestamp}",
            "run_directory": str(self.run_dir),
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0,
            "total_duration": 0,
            "test_results": [],
            "system_info": {
                "python_version": sys.version,
                "working_directory": str(Path.cwd()),
                "platform": sys.platform
            }
        }
        
    def print_banner(self):
        """Print an attractive banner"""
        print("\n" + "🚀" * 40)
        print("🧪 PDF SEARCH SYSTEM - ONE COMMAND TEST SUITE 🧪")
        print("🚀" * 40)
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🐍 Python: {sys.version.split()[0]}")
        print(f"📂 Directory: {self.tests_dir}")
        print(f"📊 Results: {self.run_dir}")
        print("🚀" * 40 + "\n")
        
    def check_and_install_dependencies(self):
        """Check and install required dependencies"""
        print("🔍 Checking dependencies...")
        
        requirements_file = self.tests_dir / "test_requirements.txt"
        if not requirements_file.exists():
            print("⚠️  No test_requirements.txt found, continuing without dependency check")
            return
            
        try:
            # Read requirements
            with open(requirements_file) as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            if not requirements:
                print("✅ No dependencies required")
                return
                
            print(f"📦 Installing {len(requirements)} dependencies...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Dependencies installed successfully")
            else:
                print("⚠️  Some dependencies may have failed to install, continuing anyway...")
                
        except Exception as e:
            print(f"⚠️  Dependency installation failed: {e}")
            print("Continuing with tests anyway...")

    def run_single_test(self, test_name, test_file):
        """Run a single test file"""
        print(f"\n{'='*60}")
        print(f"🧪 RUNNING: {test_name}")
        print(f"📄 File: {test_file}")
        print("="*60)
        
        test_path = self.tests_dir / test_file
        if not test_path.exists():
            print(f"⏭️  SKIPPED: {test_file} not found")
            self.results["skipped_tests"] += 1
            return
            
        start_time = time.time()
        try:
            result = subprocess.run(
                [sys.executable, test_file],
                cwd=self.tests_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per test
            )
            
            duration = time.time() - start_time
            self.results["total_duration"] += duration
            
            # Print the test output in real-time style
            if result.stdout:
                print(result.stdout)
                
            success = result.returncode == 0
            
            # Save individual test output to file
            test_output_file = self.run_dir / f"{test_file.replace('.py', '')}_output.txt"
            with open(test_output_file, 'w') as f:
                f.write(f"Test: {test_name}\n")
                f.write(f"File: {test_file}\n")
                f.write(f"Duration: {duration:.2f}s\n")
                f.write(f"Return Code: {result.returncode}\n")
                f.write(f"Success: {success}\n")
                f.write("="*60 + "\n")
                f.write("STDOUT:\n")
                f.write(result.stdout or "(no output)\n")
                if result.stderr:
                    f.write("\nSTDERR:\n")
                    f.write(result.stderr)
            
            # Create test result record
            test_result = {
                "test_name": test_name,
                "test_file": test_file,
                "success": success,
                "duration": round(duration, 2),
                "return_code": result.returncode,
                "has_output": bool(result.stdout),
                "has_errors": bool(result.stderr),
                "output_file": str(test_output_file)
            }
            
            if result.stderr and not success:
                print(f"\n❌ ERRORS:\n{result.stderr}")
                test_result["stderr"] = result.stderr
            
            # Print result
            status_emoji = "✅" if success else "❌"
            status_text = "PASSED" if success else "FAILED"
            print(f"\n{status_emoji} {test_name} {status_text} ({duration:.2f}s)")
            
            if success:
                self.results["passed_tests"] += 1
            else:
                self.results["failed_tests"] += 1
                
            self.results["test_results"].append(test_result)
            self.results["total_tests"] += 1
            
        except subprocess.TimeoutExpired:
            duration = 300
            self.results["total_duration"] += duration
            print(f"⏰ TIMEOUT: {test_name} (exceeded 5 minutes)")
            
            test_result = {
                "test_name": test_name,
                "test_file": test_file,
                "success": False,
                "duration": duration,
                "return_code": -1,
                "error": "Timeout"
            }
            
            self.results["test_results"].append(test_result)
            self.results["failed_tests"] += 1
            self.results["total_tests"] += 1
            
        except Exception as e:
            duration = time.time() - start_time
            self.results["total_duration"] += duration
            print(f"💥 ERROR: {test_name} - {str(e)}")
            
            test_result = {
                "test_name": test_name,
                "test_file": test_file,
                "success": False,
                "duration": round(duration, 2),
                "return_code": -1,
                "error": str(e)
            }
            
            self.results["test_results"].append(test_result)
            self.results["failed_tests"] += 1
            self.results["total_tests"] += 1

    def print_final_summary(self):
        """Print beautiful final summary"""
        total = self.results["total_tests"]
        passed = self.results["passed_tests"]
        failed = self.results["failed_tests"]
        skipped = self.results["skipped_tests"]
        duration = self.results["total_duration"]
        
        print("\n" + "🎯" * 50)
        print("📊 FINAL TEST SUMMARY")
        print("🎯" * 50)
        
        print(f"⏱️  Total Time:    {duration:.2f} seconds")
        print(f"🧪 Total Tests:    {total}")
        print(f"✅ Passed:         {passed}")
        print(f"❌ Failed:         {failed}")
        print(f"⏭️  Skipped:        {skipped}")
        
        if total > 0:
            success_rate = (passed / total) * 100
            print(f"📈 Success Rate:   {success_rate:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        print("-" * 50)
        
        for i, test in enumerate(self.results["test_results"], 1):
            status = "✅ PASS" if test["success"] else "❌ FAIL"
            name = test["test_name"][:30]  # Truncate long names
            duration = test["duration"]
            print(f"{i:2d}. {status} {name:<30} ({duration:>6.2f}s)")
        
        print("-" * 50)
        
        # Overall status
        if failed == 0 and total > 0:
            print("🎉 SUCCESS: All tests passed! System is operational! 🎉")
            exit_code = 0
        elif total == 0:
            print("⚠️  WARNING: No tests were run!")
            exit_code = 1
        else:
            print(f"💥 FAILURE: {failed} test(s) failed!")
            exit_code = 1
        
        # Save comprehensive results to run directory
        summary_file = self.run_dir / "test_summary.json"
        detailed_file = self.run_dir / "test_detailed_results.txt"
        
        try:
            # Save JSON results
            with open(summary_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            
            # Save detailed text summary
            with open(detailed_file, 'w') as f:
                f.write("PDF SEARCH SYSTEM - TEST RUN SUMMARY\n")
                f.write("="*60 + "\n")
                f.write(f"Run Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Run Directory: {self.run_dir}\n\n")
                
                f.write("OVERALL RESULTS:\n")
                f.write(f"Total Time:    {duration:.2f} seconds\n")
                f.write(f"Total Tests:   {total}\n")
                f.write(f"Passed:        {passed}\n")
                f.write(f"Failed:        {failed}\n")
                f.write(f"Skipped:       {skipped}\n")
                
                if total > 0:
                    success_rate = (passed / total) * 100
                    f.write(f"Success Rate:  {success_rate:.1f}%\n")
                
                f.write("\n" + "="*60 + "\n")
                f.write("DETAILED TEST RESULTS:\n")
                f.write("="*60 + "\n")
                
                for i, test in enumerate(self.results["test_results"], 1):
                    status = "PASS" if test["success"] else "FAIL"
                    f.write(f"\n{i}. {test['test_name']}\n")
                    f.write(f"   File: {test['test_file']}\n")
                    f.write(f"   Status: {status}\n")
                    f.write(f"   Duration: {test['duration']:.2f}s\n")
                    f.write(f"   Return Code: {test['return_code']}\n")
                    if 'output_file' in test:
                        f.write(f"   Output File: {test['output_file']}\n")
                    if 'error' in test:
                        f.write(f"   Error: {test['error']}\n")
                    f.write("   " + "-"*50 + "\n")
            
            print(f"💾 Results saved to: {self.run_dir}")
            print(f"📊 Summary: {summary_file}")
            print(f"📋 Details: {detailed_file}")
            
        except Exception as e:
            print(f"⚠️  Could not save results: {e}")
        
        # Also save legacy results file for backwards compatibility
        legacy_results_file = self.tests_dir / "complete_test_results.json"
        try:
            with open(legacy_results_file, 'w') as f:
                json.dump(self.results, f, indent=2)
        except Exception:
            pass  # Non-critical
        
        print("🎯" * 50)
        return exit_code

    def run_all_tests(self):
        """Run the complete test suite"""
        self.print_banner()
        self.check_and_install_dependencies()
        
        # Define all available tests
        test_suite = [
            ("Quick Comprehensive Test", "test_quick.py"),
            ("Simple Validation Test", "test_simple.py"),
            ("Advanced Performance Test", "test_advanced.py"),
            ("System Integration Test", "test_system.py"),
            ("Comprehensive Professional Test", "test_comprehensive.py"),
            ("Table PDF Processing", "test_table_pdf.py"),
            ("Table Simple Functionality", "test_table_simple.py"),
            ("Table Validation", "test_table_validation.py")
        ]
        
        print(f"\n🚀 Starting {len(test_suite)} test suites...\n")
        
        # Run each test
        for test_name, test_file in test_suite:
            self.run_single_test(test_name, test_file)
        
        # Print final summary and exit
        return self.print_final_summary()

def main():
    """Main entry point"""
    # Change to script directory if not already there
    script_dir = Path(__file__).parent
    if Path.cwd() != script_dir:
        print(f"📂 Changing to tests directory: {script_dir}")
        os.chdir(script_dir)
    
    # Run the test suite
    test_suite = OneCommandTestSuite()
    exit_code = test_suite.run_all_tests()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()