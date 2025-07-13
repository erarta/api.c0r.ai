#!/usr/bin/env python3
"""
Integration Tests Runner for c0r.ai API
Tests external services and connections
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "api.c0r.ai" / "app"))

def run_test_script(script_path):
    """Run a test script and return its result"""
    try:
        print(f"\n{'='*60}")
        print(f"🧪 Running: {script_path}")
        print(f"{'='*60}")
        
        # Change to the script directory
        script_dir = os.path.dirname(script_path)
        if script_dir:
            os.chdir(script_dir)
        
        # Run the script
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=False, 
                              text=True)
        
        if result.returncode == 0:
            print(f"✅ {script_path} - PASSED")
            return True
        else:
            print(f"❌ {script_path} - FAILED")
            return False
            
    except Exception as e:
        print(f"❌ {script_path} - ERROR: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 c0r.ai Integration Tests Runner")
    print("="*60)
    
    # Get the integration tests directory
    integration_dir = Path(__file__).parent / "integration"
    
    # List of test scripts to run
    test_scripts = [
        "test_db_connection.py",
        "test_bot_connection.py", 
        "test_payment_simple.py",
        "test_telegram_payments.py",
        "test_yookassa_integration.py"
    ]
    
    results = []
    
    # Run each test script
    for script in test_scripts:
        script_path = integration_dir / script
        if script_path.exists():
            success = run_test_script(str(script_path))
            results.append((script, success))
        else:
            print(f"❌ Script not found: {script_path}")
            results.append((script, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 INTEGRATION TESTS SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed
    
    for script, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {script}")
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All integration tests passed!")
        return True
    else:
        print(f"\n⚠️  {failed} integration test(s) failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 