
import csv
import json

CSV_FILE = "lecturers.csv"
JSON_FILE = "lecture.json"

def csv_to_json():
    lecturers_list = []

    with open(CSV_FILE, "r", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            lecturer = {
                "name": row.get("Họ tên", "").strip(),
                "title": row.get("Chức danh", "").strip(),
                "unit": row.get("Đơn vị", "").strip(),
                "email": row.get("Email", "").strip(),
                "phone": row.get("Điện thoại", "").strip(),
                "education": row.get("Đào tạo", "").strip(),
                "research": row.get("Nghiên cứu", "").strip(),
                "fields": row.get("Lĩnh vực nghiên cứu", "").strip()
            }
            lecturers_list.append(lecturer)

    with open(JSON_FILE, "w", encoding="utf-8") as json_file:
        json.dump(lecturers_list, json_file, ensure_ascii=False, indent=4)

    print("🎉 Đã tạo file lecture.json thành công!")

if __name__ == "__main__":
    csv_to_json()
