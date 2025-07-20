#!/usr/bin/env python3
"""
Quick syntax verification for critical files
"""
import sys
import os
import ast

def check_syntax(file_path):
    """Check Python syntax for a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Parse the AST to check syntax
        ast.parse(source)
        print(f"✅ {file_path} - Syntax OK")
        return True
    except SyntaxError as e:
        print(f"❌ {file_path} - Syntax Error: {e}")
        return False
    except Exception as e:
        print(f"⚠️ {file_path} - Error: {e}")
        return False

def main():
    """Check syntax of critical files"""
    print("🔍 Checking syntax of critical files...")
    
    files_to_check = [
        "api.c0r.ai/app/handlers/commands.py",
        "api.c0r.ai/app/handlers/recipe.py", 
        "api.c0r.ai/app/handlers/keyboards.py",
        "api.c0r.ai/app/bot.py",
        "tests/unit/test_recipe_generation.py",
        "tests/unit/test_profile_extended.py",
        "tests/integration/test_recipe_integration.py"
    ]
    
    all_good = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            if not check_syntax(file_path):
                all_good = False
        else:
            print(f"⚠️ {file_path} - File not found")
    
    if all_good:
        print("\n🎉 All files have valid syntax!")
        return True
    else:
        print("\n❌ Some files have syntax errors!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)