"""
RAG Backend package initialization
"""

import os
import sys

# Add the parent directory to sys.path to allow imports from sibling packages
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
