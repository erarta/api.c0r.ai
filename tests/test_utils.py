"""
Shared utilities for test imports and setup
"""
import sys
import os

def setup_test_imports():
    """Standard import path setup for all tests"""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Add specific paths if needed
    api_path = os.path.join(project_root, 'api.c0r.ai')
    if api_path not in sys.path:
        sys.path.insert(0, api_path)

# Call this at module level in each test file
setup_test_imports()