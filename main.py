from pathlib import Path

print("File Preparation Toolkit")

for file in Path(".").iterdir():
    print(file.name)