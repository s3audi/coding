# coding_json_to_py_files.py
import json
import os

# JSON dosyasının yolunu belirtin
json_path = "jsoncoding.json"

# JSON'u yükle
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Hangi projeyi dışarıya yazmak istiyorsunuz?
project_key = "veri_analizi"  # veya "dashboard" veya başka bir anahtar

project = data["files"] if "files" in data else data["projects"][project_key]["files"]

# Eğer anahtar doğrudan "files" ise (ör: export edilen tek proje)
if "files" in data:
    files = data["files"]
else:
    files = data["projects"][project_key]["files"]

# Her dosyayı kaydet
for file_name, file_content in files.items():
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(file_content)
    print(f"{file_name} oluşturuldu.")
