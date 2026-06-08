from pathlib import Path
import json
import textwrap

# ============================================================
# Create project folder
# ============================================================

PROJECT = Path("fine-tuning-ticket-classifier")
DATA = PROJECT / "data"

DATA.mkdir(parents=True, exist_ok=True)

# ============================================================
# 1. Create sample train.jsonl and validation.jsonl
# ============================================================

system_prompt = """
You are an IT support ticket classifier.
Classify the ticket into exactly one of these categories:
access_management, incident_security, network_connectivity, hardware_support, software_support, service_request.
Return only the category name.
""".strip()

train_examples = [
    ("I cannot log in to my corporate account.", "access_management"),
    ("Please reset MFA for my user account.", "access_management"),
    ("I need access to the finance application.", "access_management"),
    ("Please remove access for an employee who left.", "access_management"),

    ("I received a suspicious phishing email.", "incident_security"),
    ("My antivirus detected malware on my laptop.", "incident_security"),
    ("There are many failed login attempts on my account.", "incident_security"),
    ("A confidential file may have been shared externally.", "incident_security"),

    ("The Wi-Fi keeps disconnecting.", "network_connectivity"),
    ("VPN connects but internal applications are unreachable.", "network_connectivity"),
    ("The internet is very slow in the office.", "network_connectivity"),
    ("The network printer is not reachable.", "network_connectivity"),

    ("My laptop screen is broken.", "hardware_support"),
    ("My keyboard is not working.", "hardware_support"),
    ("The docking station does not detect my monitors.", "hardware_support"),
    ("My laptop battery drains very quickly.", "hardware_support"),

    ("Outlook does not open.", "software_support"),
    ("Excel crashes when I open a file.", "software_support"),
    ("The CRM application shows an error.", "software_support"),
    ("Please install Python on my computer.", "software_support"),

    ("Please prepare a laptop for a new joiner.", "service_request"),
    ("I need a new headset.", "service_request"),
    ("Please set up a meeting room projector.", "service_request"),
    ("Please install approved software for my team.", "service_request"),
]

validation_examples = [
    ("My account is locked.", "access_management"),
    ("I clicked a suspicious link.", "incident_security"),
    ("VPN is connected but I cannot access servers.", "network_connectivity"),
    ("My mouse is not working.", "hardware_support"),
    ("The HR application freezes.", "software_support"),
    ("Please prepare equipment for onboarding.", "service_request"),
]

def write_jsonl(path, examples):
    with open(path, "w", encoding="utf-8") as f:
        for ticket, label in examples:
            row = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Ticket: {ticket}"},
                    {"role": "assistant", "content": label}
                ]
            }
            f.write(json.dumps(row) + "\n")

write_jsonl(DATA / "train.jsonl", train_examples)
write_jsonl(DATA / "validation.jsonl", validation_examples)

# ============================================================
# 2. Create .env
# ============================================================

(PROJECT / ".env").write_text("""
OPENAI_API_KEY=replace_with_your_openai_api_key
BASE_MODEL=gpt-4.1-mini-2025-04-14
FINE_TUNED_MODEL=
""".strip(), encoding="utf-8")

# ============================================================
# 3. Create requirements.txt
# ============================================================

(PROJECT / "requirements.txt").write_text("""
openai
python-dotenv
gradio
""".strip(), encoding="utf-8")

# ============================================================
# 4. Create validate_data.py
# ============================================================

(PROJECT / "validate_data.py").write_text(r'''
import json
from pathlib import Path
from collections import Counter

ALLOWED_LABELS = {
    "access_management",
    "incident_security",
    "network_connectivity",
    "hardware_support",
    "software_support",
    "service_request",
}

def validate_jsonl(path):
    path = Path(path)
    errors = []
    labels = Counter()

    if not path.exists():
        print(f"[ERROR] File not found: {path}")
        return False

    lines = path.read_text(encoding="utf-8").splitlines()

    for i, line in enumerate(lines, start=1):
        try:
            obj = json.loads(line)
        except Exception as e:
            errors.append(f"Line {i}: Invalid JSON - {e}")
            continue

        if "messages" not in obj:
            errors.append(f"Line {i}: Missing 'messages'")
            continue

        messages = obj["messages"]

        if not isinstance(messages, list) or len(messages) < 3:
            errors.append(f"Line {i}: messages must contain system, user, assistant")
            continue

        if messages[-1]["role"] != "assistant":
            errors.append(f"Line {i}: Last message must be assistant")
            continue

        label = messages[-1]["content"].strip()

        if label not in ALLOWED_LABELS:
            errors.append(f"Line {i}: Invalid label: {label}")
        else:
            labels[label] += 1

    if errors:
        print("[FAILED] Validation errors:")
        for error in errors:
            print(error)
        return False

    print(f"[OK] {path} is valid.")
    print("Label distribution:")
    for label, count in labels.items():
        print(f"- {label}: {count}")

    return True

if __name__ == "__main__":
    train_ok = validate_jsonl("data/train.jsonl")
    validation_ok = validate_jsonl("data/validation.jsonl")

    if train_ok and validation_ok:
        print("[SUCCESS] All files are valid.")
    else:
        raise SystemExit("[ERROR] Fix your JSONL files.")
'''.strip(), encoding="utf-8")

# ============================================================
# 5. Create train.py
# ============================================================

(PROJECT / "train.py").write_text(r'''
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_MODEL = os.getenv("BASE_MODEL", "gpt-4.1-mini-2025-04-14")

TRAIN_FILE = "data/train.jsonl"
VALIDATION_FILE = "data/validation.jsonl"

def upload_file(path):
    print(f"[INFO] Uploading {path}...")
    uploaded_file = client.files.create(
        file=open(path, "rb"),
        purpose="fine-tune"
    )
    print(f"[OK] Uploaded file ID: {uploaded_file.id}")
    return uploaded_file.id

def create_fine_tuning_job():
    training_file_id = upload_file(TRAIN_FILE)
    validation_file_id = upload_file(VALIDATION_FILE)

    print("[INFO] Creating fine-tuning job...")

    job = client.fine_tuning.jobs.create(
        training_file=training_file_id,
        validation_file=validation_file_id,
        model=BASE_MODEL,
        suffix="ticket-classifier"
    )

    Path("job_id.txt").write_text(job.id, encoding="utf-8")

    print(f"[SUCCESS] Fine-tuning job created: {job.id}")
    print("[INFO] Job ID saved in job_id.txt")

    return job.id

def wait_for_job(job_id):
    print("[INFO] Waiting for fine-tuning job to finish...")

    while True:
        job = client.fine_tuning.jobs.retrieve(job_id)

        print(f"[STATUS] {job.status}")

        if job.status == "succeeded":
            model_id = job.fine_tuned_model
            Path("fine_tuned_model.txt").write_text(model_id, encoding="utf-8")
            print(f"[SUCCESS] Fine-tuned model created: {model_id}")
            print("[INFO] Model ID saved in fine_tuned_model.txt")
            break

        if job.status in ["failed", "cancelled"]:
            print("[ERROR] Fine-tuning failed or was cancelled.")
            print(job)
            break

        time.sleep(30)

if __name__ == "__main__":
    job_id = create_fine_tuning_job()
    wait_for_job(job_id)
'''.strip(), encoding="utf-8")

# ============================================================
# 6. Create test_model.py
# ============================================================

(PROJECT / "test_model.py").write_text(r'''
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are an IT support ticket classifier.
Classify the ticket into exactly one of these categories:
access_management, incident_security, network_connectivity, hardware_support, software_support, service_request.
Return only the category name.
""".strip()

def get_model_id():
    env_model = os.getenv("FINE_TUNED_MODEL")

    if env_model:
        return env_model

    if Path("fine_tuned_model.txt").exists():
        return Path("fine_tuned_model.txt").read_text(encoding="utf-8").strip()

    raise Exception("No fine-tuned model found. Train the model first.")

def classify_ticket(ticket):
    model_id = get_model_id()

    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Ticket: {ticket}"}
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    ticket = "The VPN connects but I cannot access internal applications."
    label = classify_ticket(ticket)

    print("Ticket:", ticket)
    print("Predicted label:", label)
'''.strip(), encoding="utf-8")

# ============================================================
# 7. Create app.py
# ============================================================

(PROJECT / "app.py").write_text(r'''
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are an IT support ticket classifier.
Classify the ticket into exactly one of these categories:
access_management, incident_security, network_connectivity, hardware_support, software_support, service_request.
Return only the category name.
""".strip()

def get_model_id():
    env_model = os.getenv("FINE_TUNED_MODEL")

    if env_model:
        return env_model

    if Path("fine_tuned_model.txt").exists():
        return Path("fine_tuned_model.txt").read_text(encoding="utf-8").strip()

    return os.getenv("BASE_MODEL")

def classify(ticket):
    model_id = get_model_id()

    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Ticket: {ticket}"}
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip()

demo = gr.Interface(
    fn=classify,
    inputs=gr.Textbox(label="Ticket description", lines=5),
    outputs=gr.Textbox(label="Predicted category"),
    title="Fine-Tuned Ticket Classifier",
    description="Classifies IT support tickets into predefined categories."
)

if __name__ == "__main__":
    demo.launch(share=True)
'''.strip(), encoding="utf-8")

# ============================================================
# 8. Create Dockerfile
# ============================================================

(PROJECT / "Dockerfile").write_text(r'''
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["python", "app.py"]
'''.strip(), encoding="utf-8")

# ============================================================
# 9. Create README.md
# ============================================================

(PROJECT / "README.md").write_text(r'''
# Fine-Tuning Ticket Classifier

This project fine-tunes an OpenAI model to classify IT support tickets.

## Categories

- access_management
- incident_security
- network_connectivity
- hardware_support
- software_support
- service_request

## Commands

Install dependencies:

```bash
pip install -r requirements.txt
