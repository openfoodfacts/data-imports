#!/usr/bin/env python3
"""
Main runner script for Serbian price database import.
This script orchestrates the full workflow:
1. Harvest data from data.gov.rs
2. Process the data
3. Generate outputs for Open Food Facts and Open Prices

Usage:
    python3 run_import.py [--test-only]
    
Options:
    --test-only    Run in test mode (create test data instead of harvesting)
"""

import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent


def log(message):
    """Print timestamped log message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def run_script(script_name, description):
    """Run a Python script and return success status."""
    log(f"Starting: {description}")
    
    script_path = SCRIPT_DIR / script_name
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True
    )
    
    # Print output
    if result.stdout:
        print(result.stdout)
    
    if result.returncode != 0:
        log(f"ERROR in {script_name}")
        if result.stderr:
            print(result.stderr)
        return False
    
    log(f"Completed: {description}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Serbian Price Database Import Runner"
    )
    parser.add_argument(
        '--test-only',
        action='store_true',
        help='Run in test mode (no actual data download)'
    )
    
    args = parser.parse_args()
    
    log("=" * 60)
    log("Serbian Price Database Import - Full Workflow")
    log("=" * 60)
    
    if args.test_only:
        log("Running in TEST MODE")
        if not run_script("test_workflow.py", "Test Workflow"):
            return 1
    else:
        # Step 1: Harvest data
        if not run_script("harvest_data.py", "Data Harvesting"):
            log("Harvest failed. Aborting.")
            return 1
        
        # Step 2: Process data
        if not run_script("process_data.py", "Data Processing"):
            log("Processing failed. Aborting.")
            return 1
    
    log("=" * 60)
    log("Import workflow completed successfully!")
    log("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
