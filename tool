
import csv
import json
from pathlib import Path

CSV_FILE = Path("lecturers.csv")
JSON_FILE = Path("lecturers.json")

def split_field(value):
    if not value:
        return []
    return [v.strip() for v in value.split("|") if v.strip()]

lecturers = []

with open(CSV_FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        lecturers.append({
            "key": row["key"],
            "name": row["name"],
            "title": row["title"],
            "dept": row["dept"],
            "img": row["img"],
            "email": row["email"],
            "phone": row["phone"],
            "office": row["office"],
            "train": split_field(row.get("train")),
            "work": split_field(row.get("work")),
            "teach": split_field(row.get("teach")),
            "area": split_field(row.get("area")),
        })

with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump(lecturers, f, ensure_ascii=False, indent=2)

print("✅ lecturers.json generated successfully")
