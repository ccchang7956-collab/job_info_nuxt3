import sys
import os

# Add the current directory to sys.path to simulate running from backend/
sys.path.append(os.getcwd())

try:
    from app.utils.format_utils import format_roc_date
    print("Import successful!")
except Exception as e:
    print(f"Import failed: {e}")
