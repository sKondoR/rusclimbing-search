# run_tests.py
import unittest
import sys
import os

# Добавляем корневую директорию в sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_parser.py')
    suite = loader.discover(start_dir, pattern='test_parser.py')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
