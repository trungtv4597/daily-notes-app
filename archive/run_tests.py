#!/usr/bin/env python3
"""
Test runner script for the Daily Notes application.
"""
import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and print the result."""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def main():
    """Main function to run tests and quality checks."""
    print("Daily Notes Application - Test Runner")
    print("====================================")
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("Error: Please run this script from the project root directory.")
        sys.exit(1)
    
    # List of commands to run
    commands = [
        ("python -m pytest tests/ -v", "Running unit tests"),
        ("python -m pytest tests/ --cov=src --cov-report=term-missing", "Running tests with coverage"),
        ("python -c \"from src.components.database import db_manager; print('Database import:', 'OK' if db_manager else 'FAILED')\"", "Testing imports"),
        ("python -c \"from src.calculations.utils import validate_note_content; print('Utils import:', 'OK' if validate_note_content else 'FAILED')\"", "Testing utility imports"),
    ]
    
    # Optional quality checks (only if tools are installed)
    optional_commands = [
        ("black --check .", "Code formatting check (Black)"),
        ("flake8 src/ tests/", "Linting check (flake8)"),
        ("mypy src/", "Type checking (mypy)"),
    ]
    
    success_count = 0
    total_count = len(commands)
    
    # Run required commands
    for command, description in commands:
        if run_command(command, description):
            success_count += 1
    
    # Run optional commands (don't count failures)
    print(f"\n{'='*50}")
    print("Running optional quality checks...")
    print(f"{'='*50}")
    
    for command, description in optional_commands:
        try:
            run_command(command, description)
        except Exception as e:
            print(f"Skipping {description}: {e}")
    
    # Summary
    print(f"\n{'='*50}")
    print("SUMMARY")
    print(f"{'='*50}")
    print(f"Passed: {success_count}/{total_count} required tests")
    
    if success_count == total_count:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
