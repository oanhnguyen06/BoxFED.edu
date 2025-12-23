import time
from pathlib import Path
import subprocess

CSV_FILE = Path("lecturers.csv")
SCRIPT = "csv_to_json.py"

print(" Watching CSV for changes...")

last_modified = CSV_FILE.stat().st_mtime

while True:
    time.sleep(2)
    current_modified = CSV_FILE.stat().st_mtime

    if current_modified != last_modified:
        subprocess.run(["python", SCRIPT])
        print(" CSV changed → JSON updated")
        last_modified = current_modified
