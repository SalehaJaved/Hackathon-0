"""
Test Runner for AI Employee Watchers

This script runs all watcher scripts in test mode to verify functionality
without starting the full orchestrator.
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path

def setup_logging():
    """Set up logging for the test runner"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger('TestRunner')

def run_with_test_mode(script_name, env_vars=None):
    """Run a script with TEST_MODE environment variables"""
    if env_vars is None:
        env_vars = {}

    # Set up environment with test mode enabled
    env = os.environ.copy()
    env.update(env_vars)

    try:
        result = subprocess.run([
            sys.executable, script_name
        ], env=env, capture_output=True, text=True, timeout=120)

        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': 'Process timed out after 120 seconds',
            'returncode': -1
        }

def main():
    logger = setup_logging()
    base_path = Path(__file__).parent
    results = {}

    logger.info("Starting AI Employee Watcher Test Runner")
    logger.info("=" * 50)

    # Test LinkedIn Watcher
    logger.info("Testing LinkedIn Watcher...")
    linkedin_result = run_with_test_mode(
        'linkedin_watcher.py',
        {'LINKEDIN_TEST_MODE': 'True', 'LINKEDIN_HEADLESS': 'True'}
    )
    results['LinkedIn'] = linkedin_result
    logger.info(f"LinkedIn Watcher: {'PASS' if linkedin_result['success'] else 'FAIL'}")
    if not linkedin_result['success']:
        logger.error(f"LinkedIn stderr: {linkedin_result['stderr'][:500]}...")

    # Test WhatsApp Watcher
    logger.info("Testing WhatsApp Watcher...")
    whatsapp_result = run_with_test_mode(
        'whatsapp_watcher.py',
        {'WHATSAPP_TEST_MODE': 'True'}
    )
    results['WhatsApp'] = whatsapp_result
    logger.info(f"WhatsApp Watcher: {'PASS' if whatsapp_result['success'] else 'FAIL'}")
    if not whatsapp_result['success']:
        logger.error(f"WhatsApp stderr: {whatsapp_result['stderr'][:500]}...")

    # Test Gmail Watcher
    logger.info("Testing Gmail Watcher...")
    gmail_result = run_with_test_mode(
        'gmail_watcher.py',
        {'GMAIL_TEST_MODE': 'True'}
    )
    results['Gmail'] = gmail_result
    logger.info(f"Gmail Watcher: {'PASS' if gmail_result['success'] else 'FAIL'}")
    if not gmail_result['success']:
        logger.error(f"Gmail stderr: {gmail_result['stderr'][:500]}...")

    # Print summary report
    logger.info("=" * 50)
    logger.info("TEST RESULTS SUMMARY:")
    logger.info(f"LinkedIn Watcher: {'PASS' if results['LinkedIn']['success'] else 'FAIL'}")
    logger.info(f"WhatsApp Watcher: {'PASS' if results['WhatsApp']['success'] else 'FAIL'}")
    logger.info(f"Gmail Watcher: {'PASS' if results['Gmail']['success'] else 'FAIL'}")

    total_passed = sum(1 for result in results.values() if result['success'])
    total_tests = len(results)
    logger.info(f"Overall: {total_passed}/{total_tests} watchers passed")

    # Detailed results
    for watcher, result in results.items():
        print(f"\n{watcher} Watcher Details:")
        print(f"  Success: {result['success']}")
        print(f"  Return code: {result['returncode']}")
        if result['stdout']:
            print(f"  Stdout (first 200 chars): {result['stdout'][:200]}...")
        if result['stderr']:
            print(f"  Stderr (first 200 chars): {result['stderr'][:200]}...")

    # Final validation
    all_passed = all(result['success'] for result in results.values())
    logger.info(f"\nAll Watchers Test: {'PASS' if all_passed else 'FAIL'}")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())