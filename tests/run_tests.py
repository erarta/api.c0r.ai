"""
Test runner script for c0r.AI ML Service
Provides convenient test execution with different configurations
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_command(cmd, description=""):
    """Run a command and handle output"""
    print(f"\n{'='*60}")
    if description:
        print(f"🚀 {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode != 0:
            print(f"❌ Command failed with return code {result.returncode}")
            return False
        else:
            print("✅ Command completed successfully")
            return True
            
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False


def run_unit_tests(verbose=False, coverage=False, specific_test=None):
    """Run unit tests"""
    cmd = ["python", "-m", "pytest", "tests/unit/"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend([
            "--cov=services/ml",
            "--cov-report=html",
            "--cov-report=term",
            "--cov-fail-under=85"
        ])
    
    if specific_test:
        cmd = ["python", "-m", "pytest", specific_test]
    
    cmd.extend(["-x", "--tb=short"])  # Stop on first failure, short traceback
    
    return run_command(cmd, "Running Unit Tests")


def run_integration_tests(verbose=False, specific_test=None):
    """Run integration tests"""
    cmd = ["python", "-m", "pytest", "tests/integration/", "-m", "integration"]
    
    if verbose:
        cmd.append("-v")
    
    if specific_test:
        cmd = ["python", "-m", "pytest", specific_test, "-m", "integration"]
    
    cmd.extend(["-x", "--tb=short"])
    
    return run_command(cmd, "Running Integration Tests")


def run_all_tests(verbose=False, coverage=False):
    """Run all tests"""
    cmd = ["python", "-m", "pytest", "tests/"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend([
            "--cov=services/ml",
            "--cov-report=html",
            "--cov-report=term",
            "--cov-fail-under=80"  # Lower threshold for all tests
        ])
    
    cmd.extend(["--tb=short"])
    
    return run_command(cmd, "Running All Tests")


def run_specific_test_file(test_file, verbose=False):
    """Run a specific test file"""
    cmd = ["python", "-m", "pytest", test_file]
    
    if verbose:
        cmd.append("-v")
    
    cmd.extend(["-x", "--tb=short"])
    
    return run_command(cmd, f"Running Specific Test: {test_file}")


def run_tests_by_marker(marker, verbose=False):
    """Run tests by marker"""
    cmd = ["python", "-m", "pytest", "tests/", "-m", marker]
    
    if verbose:
        cmd.append("-v")
    
    cmd.extend(["-x", "--tb=short"])
    
    return run_command(cmd, f"Running Tests with Marker: {marker}")


def run_performance_tests(verbose=False):
    """Run performance tests"""
    cmd = ["python", "-m", "pytest", "tests/", "-m", "slow", "--durations=10"]
    
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd, "Running Performance Tests")


def lint_code():
    """Run code linting"""
    print("\n🔍 Running Code Linting...")
    
    # Check if flake8 is available
    try:
        subprocess.run(["flake8", "--version"], capture_output=True, check=True)
        flake8_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        flake8_available = False
    
    # Check if black is available
    try:
        subprocess.run(["black", "--version"], capture_output=True, check=True)
        black_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        black_available = False
    
    success = True
    
    if flake8_available:
        cmd = ["flake8", "services/ml/", "--max-line-length=100", "--ignore=E203,W503"]
        if not run_command(cmd, "Running Flake8 Linting"):
            success = False
    else:
        print("⚠️ Flake8 not available, skipping linting")
    
    if black_available:
        cmd = ["black", "--check", "--diff", "services/ml/"]
        if not run_command(cmd, "Checking Black Formatting"):
            success = False
    else:
        print("⚠️ Black not available, skipping format checking")
    
    return success


def format_code():
    """Format code with black"""
    try:
        subprocess.run(["black", "--version"], capture_output=True, check=True)
        cmd = ["black", "services/ml/"]
        return run_command(cmd, "Formatting Code with Black")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ Black not available, cannot format code")
        return False


def generate_coverage_report():
    """Generate detailed coverage report"""
    cmd = [
        "python", "-m", "pytest", "tests/",
        "--cov=services/ml",
        "--cov-report=html",
        "--cov-report=xml",
        "--cov-report=term-missing"
    ]
    
    success = run_command(cmd, "Generating Coverage Report")
    
    if success:
        print("\n📊 Coverage reports generated:")
        print("  - HTML: htmlcov/index.html")
        print("  - XML: coverage.xml")
    
    return success


def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n🔍 Checking Dependencies...")
    
    required_packages = [
        "pytest",
        "pytest-cov",
        "loguru",
        "requests"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    print("\n✅ All required dependencies are installed")
    return True


def clean_test_artifacts():
    """Clean test artifacts and cache"""
    print("\n🧹 Cleaning Test Artifacts...")
    
    artifacts_to_clean = [
        ".pytest_cache",
        "__pycache__",
        "htmlcov",
        "coverage.xml",
        ".coverage"
    ]
    
    for artifact in artifacts_to_clean:
        artifact_path = project_root / artifact
        if artifact_path.exists():
            if artifact_path.is_dir():
                import shutil
                shutil.rmtree(artifact_path)
                print(f"🗑️ Removed directory: {artifact}")
            else:
                artifact_path.unlink()
                print(f"🗑️ Removed file: {artifact}")
    
    # Clean __pycache__ directories recursively
    for pycache_dir in project_root.rglob("__pycache__"):
        if pycache_dir.is_dir():
            import shutil
            shutil.rmtree(pycache_dir)
            print(f"🗑️ Removed: {pycache_dir}")
    
    print("✅ Cleanup completed")


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="c0r.AI ML Service Test Runner")
    
    parser.add_argument(
        "command",
        choices=[
            "unit", "integration", "all", "lint", "format", "coverage",
            "clean", "deps", "performance", "file", "marker"
        ],
        help="Test command to run"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "-c", "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "-f", "--file",
        type=str,
        help="Specific test file to run"
    )
    
    parser.add_argument(
        "-m", "--marker",
        type=str,
        help="Run tests with specific marker"
    )
    
    parser.add_argument(
        "--no-deps-check",
        action="store_true",
        help="Skip dependency check"
    )
    
    args = parser.parse_args()
    
    print("🧪 c0r.AI ML Service Test Runner")
    print(f"Project Root: {project_root}")
    
    # Check dependencies unless skipped
    if not args.no_deps_check and args.command not in ["clean", "deps"]:
        if not check_dependencies():
            print("\n❌ Dependency check failed. Use --no-deps-check to skip.")
            return 1
    
    success = True
    
    if args.command == "unit":
        success = run_unit_tests(args.verbose, args.coverage, args.file)
    
    elif args.command == "integration":
        success = run_integration_tests(args.verbose, args.file)
    
    elif args.command == "all":
        success = run_all_tests(args.verbose, args.coverage)
    
    elif args.command == "lint":
        success = lint_code()
    
    elif args.command == "format":
        success = format_code()
    
    elif args.command == "coverage":
        success = generate_coverage_report()
    
    elif args.command == "clean":
        clean_test_artifacts()
    
    elif args.command == "deps":
        success = check_dependencies()
    
    elif args.command == "performance":
        success = run_performance_tests(args.verbose)
    
    elif args.command == "file":
        if not args.file:
            print("❌ --file argument required for 'file' command")
            return 1
        success = run_specific_test_file(args.file, args.verbose)
    
    elif args.command == "marker":
        if not args.marker:
            print("❌ --marker argument required for 'marker' command")
            return 1
        success = run_tests_by_marker(args.marker, args.verbose)
    
    if success:
        print("\n🎉 All operations completed successfully!")
        return 0
    else:
        print("\n💥 Some operations failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())