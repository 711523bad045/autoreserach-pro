import sys
import os

# Add backend to path
sys.path.append(os.getcwd())

try:
    print("Attempting to import app.database.models.crawl_job...")
    from app.database.models import crawl_job
    print("Import successful!")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
