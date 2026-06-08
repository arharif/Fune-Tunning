from pathlib import Path

# Project name
project = Path("fine-tuning-ticket-classifier")

# Folders
folders = [
    project / "data"
]

# Files
files = [
    project / "data" / "train.jsonl",
    project / "data" / "validation.jsonl",
    project / ".env",
    project / "requirements.txt",
    project / "validate_data.py",
    project / "train.py",
    project / "test_model.py",
    project / "app.py",
    project / "Dockerfile",
]

# Create folders
for folder in folders:
    folder.mkdir(parents=True, exist_ok=True)

# Create empty files
for file in files:
    file.touch(exist_ok=True)

print("Empty project structure created successfully:\n")

for path in sorted(project.rglob("*")):
    print(path)
