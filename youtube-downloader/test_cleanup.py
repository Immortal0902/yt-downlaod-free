import asyncio
import os
import time
from pathlib import Path

# Fix path import
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.keep_alive import cleanup_old_files, BASE_DIR, DOWNLOAD_DIR

# Mock config for testing
import app.utils.keep_alive as ka
ka.CLEANUP_INTERVAL = 1
ka.FILE_MAX_AGE = 1

async def test_cleanup():
    print("Testing Auto-Delete Logic...")
    
    # 1. Create a dummy file
    test_file = DOWNLOAD_DIR / "test_delete_me.txt"
    if not DOWNLOAD_DIR.exists():
        DOWNLOAD_DIR.mkdir()
        
    with open(test_file, "w") as f:
        f.write("I should be deleted.")
    
    print(f"Created file: {test_file}")
    
    # 2. Touch it to be old (2 seconds ago)
    past = time.time() - 5
    os.utime(test_file, (past, past))
    
    # 3. Run cleanup once
    # We run the loop for a short time
    task = asyncio.create_task(cleanup_old_files())
    await asyncio.sleep(2)
    task.cancel()
    
    # 4. Check if deleted
    if not test_file.exists():
        print("SUCCESS: File was auto-deleted.")
    else:
        print("FAIL: File still exists.")

if __name__ == "__main__":
    asyncio.run(test_cleanup())
