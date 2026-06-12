import pandas as pd
import json
from pathlib import Path

# Excel path
excel_file = r"C:\Users\guillem.maya\Desktop\Analytics\Chinese\chinese.xlsx"

# Sheet name
df = pd.read_excel(excel_file, sheet_name="shuazi")

# JSON data list
data = []

for _, row in df.iterrows():
    item = {
        "id": int(row["id"]),
        "productive": int(row["productive"]),
        "hanzi": str(row["hanzi"]),
        "definition": str(row["definition"]),
        "radical": str(row["radical"]),
        "stroke": int(row["stroke"]),
        "hsk_level": int(row["hsk_level"]),
        "coverage": round(float(row["coverage"]), 4)
    }
    data.append(item)

# Save JSON to file
excel_path = Path(excel_file)
output_file = excel_path.parent / "shuazi_hanzi.json"

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"JSON saved to: {output_file}")
print(f"Total records: {len(data)}")