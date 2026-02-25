# run_tests.py
import unittest
import sys
import os

# Добавляем корневую директорию в sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = '.'
    suite = loader.discover(start_dir, pattern='test_*.py')
    runner = unittest.TextTestRunner()
    runner.run(suite)