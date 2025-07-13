#!/usr/bin/env python3
"""
Comprehensive test runner for c0r.ai API with coverage reporting
"""

import os
import sys
import subprocess
import json
from datetime import datetime

def run_command(cmd, description):
    """Run a command and return result"""
    print(f"🔄 {description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ {description} - SUCCESS")
        return True, result.stdout
    else:
        print(f"❌ {description} - FAILED")
        print(f"Error: {result.stderr}")
        return False, result.stderr

def main():
    """Main test runner"""
    print("=" * 60)
    print("🧪 c0r.ai API Test Suite with Coverage Analysis")
    print("=" * 60)
    
    # Change to project root directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    os.chdir(project_root)
    
    # Install test dependencies
    success, _ = run_command(
        "pip install -r tests/requirements.txt",
        "Installing test dependencies"
    )
    if not success:
        print("❌ Failed to install test dependencies")
        sys.exit(1)
    
    # Create coverage directory
    os.makedirs("tests/coverage", exist_ok=True)
    
    # Run unit tests with coverage
    print("\n📋 Running Unit Tests with Coverage...")
    unit_success, unit_output = run_command(
        "python -m pytest tests/unit/ -v --cov=api.c0r.ai/app --cov=common --cov-report=html:tests/coverage/unit_html --cov-report=json:tests/coverage/unit_coverage.json --cov-report=term-missing",
        "Unit tests with coverage"
    )
    
    # Run integration tests
    print("\n🔗 Running Integration Tests...")
    integration_success, integration_output = run_command(
        "python -m pytest tests/integration/test_api_integration.py -v --cov=api.c0r.ai/app --cov=common --cov-report=html:tests/coverage/integration_html --cov-report=json:tests/coverage/integration_coverage.json --cov-report=term-missing",
        "Integration tests with coverage"
    )
    
    # Run external integration tests (external services)
    print("\n🌐 Running External Integration Tests...")
    external_success, external_output = run_command(
        "cd tests && python run_integration_tests.py",
        "External integration tests (DB, payments, etc.)"
    )
    
    # Run all tests together for combined coverage
    print("\n🎯 Running All Tests for Combined Coverage...")
    all_success, all_output = run_command(
        "python -m pytest tests/unit/ tests/integration/test_api_integration.py -v --cov=api.c0r.ai/app --cov=common --cov-report=html:tests/coverage/combined_html --cov-report=json:tests/coverage/combined_coverage.json --cov-report=term-missing --cov-fail-under=85",
        "All tests with combined coverage"
    )
    
    # Generate coverage report
    print("\n📊 Generating Coverage Report...")
    
    # Read coverage data
    coverage_file = "tests/coverage/combined_coverage.json"
    if os.path.exists(coverage_file):
        with open(coverage_file, 'r') as f:
            coverage_data = json.load(f)
        
        total_coverage = coverage_data['totals']['percent_covered']
        
        # Generate detailed report
        report_file = "tests/coverage/coverage_report.md"
        with open(report_file, 'w') as f:
            f.write("# Code Coverage Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Total Coverage**: {total_coverage:.1f}%\n\n")
            
            if total_coverage >= 85:
                f.write("✅ **PASSED** - Coverage meets minimum requirement (85%)\n\n")
            else:
                f.write("❌ **FAILED** - Coverage below minimum requirement (85%)\n\n")
            
            f.write("## Coverage by File\n\n")
            f.write("| File | Coverage | Lines | Missing |\n")
            f.write("|------|----------|-------|----------|\n")
            
            for file_path, file_data in coverage_data['files'].items():
                if 'percent_covered' in file_data:
                    coverage_percent = file_data['percent_covered']
                    total_lines = file_data['summary']['num_statements']
                    missing_lines = file_data['summary']['missing_lines']
                    
                    status = "✅" if coverage_percent >= 85 else "⚠️" if coverage_percent >= 70 else "❌"
                    f.write(f"| {file_path} | {status} {coverage_percent:.1f}% | {total_lines} | {len(missing_lines)} |\n")
            
            f.write("\n## Critical Components Coverage\n\n")
            
            critical_files = [
                'api.c0r.ai/app/handlers/nutrition.py',
                'api.c0r.ai/app/handlers/commands.py',
                'common/nutrition_calculations.py',
                'common/supabase_client.py'
            ]
            
            for file_path in critical_files:
                if file_path in coverage_data['files']:
                    file_data = coverage_data['files'][file_path]
                    coverage_percent = file_data['percent_covered']
                    status = "✅" if coverage_percent >= 85 else "❌"
                    f.write(f"- **{file_path}**: {status} {coverage_percent:.1f}%\n")
                else:
                    f.write(f"- **{file_path}**: ❌ Not covered\n")
        
        print(f"📊 Coverage report generated: {report_file}")
        print(f"📊 HTML report available: tests/coverage/combined_html/index.html")
        print(f"📊 Total coverage: {total_coverage:.1f}%")
    else:
        print("❌ Coverage data not found")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary")
    print("=" * 60)
    
    print(f"Unit Tests: {'✅ PASSED' if unit_success else '❌ FAILED'}")
    print(f"Integration Tests: {'✅ PASSED' if integration_success else '❌ FAILED'}")
    print(f"External Integration Tests: {'✅ PASSED' if external_success else '❌ FAILED'}")
    print(f"Overall Coverage: {'✅ PASSED' if all_success else '❌ FAILED'}")
    
    if os.path.exists(coverage_file):
        print(f"Code Coverage: {total_coverage:.1f}% {'✅ PASSED' if total_coverage >= 85 else '❌ FAILED'}")
    
    # Exit with appropriate code
    if all_success and external_success and total_coverage >= 85:
        print("\n🎉 All tests passed and coverage meets requirements!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed or coverage is below 85%")
        sys.exit(1)

if __name__ == "__main__":
    main() 