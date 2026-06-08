from pathlib import Path

%cd /content/fine-tuning-ticket-classifier

Path("train.py").write_text(r'''
from openai import OpenAI, PermissionDeniedError
from dotenv import load_dotenv
from pathlib import Path
import time
import json

load_dotenv()

client = OpenAI()

BASE_MODEL = "gpt-4.1-nano-2025-04-14"

TRAIN_FILE = "data/train.jsonl"
VALIDATION_FILE = "data/validation.jsonl"


def check_files():
    required_files = [TRAIN_FILE, VALIDATION_FILE, ".env"]

    for file in required_files:
        if not Path(file).exists():
            raise FileNotFoundError(f"Missing required file: {file}")

    print("[OK] Required files found.")


def upload_file(path: str):
    with open(path, "rb") as f:
        uploaded_file = client.files.create(
            file=f,
            purpose="fine-tune"
        )

    print(f"[OK] Uploaded {path}")
    print(f"[OK] File ID: {uploaded_file.id}")

    return uploaded_file.id


def create_fine_tuning_job(training_file_id: str, validation_file_id: str):
    job = client.fine_tuning.jobs.create(
        model=BASE_MODEL,
        training_file=training_file_id,
        validation_file=validation_file_id,
        suffix="cyber-ticket-classifier"
    )

    print("[OK] Fine-tuning job created.")
    print(f"[OK] Job ID: {job.id}")

    Path("job_id.txt").write_text(job.id, encoding="utf-8")

    return job.id


def monitor_job(job_id: str):
    while True:
        job = client.fine_tuning.jobs.retrieve(job_id)

        print(f"[STATUS] {job.status}")

        if job.status in ["succeeded", "failed", "cancelled"]:
            print("[FINAL STATUS]", job.status)
            print("[FINE-TUNED MODEL]", job.fine_tuned_model)

            if job.fine_tuned_model:
                Path("fine_tuned_model.txt").write_text(
                    job.fine_tuned_model,
                    encoding="utf-8"
                )
                print("[OK] Fine-tuned model saved in fine_tuned_model.txt")

            return job

        time.sleep(30)


def save_fallback_config():
    fallback_config = {
        "mode": "prompt_based_classifier",
        "reason": "Fine-tuning is not available for this OpenAI organization.",
        "base_model": BASE_MODEL,
        "note": "Use test_model.py with the base model and strict JSON prompting."
    }

    Path("model_config.json").write_text(
        json.dumps(fallback_config, indent=2),
        encoding="utf-8"
    )

    print("[FALLBACK] model_config.json created.")
    print("[FALLBACK] You can continue using a prompt-based classifier.")


if __name__ == "__main__":
    try:
        check_files()

        training_file_id = upload_file(TRAIN_FILE)
        validation_file_id = upload_file(VALIDATION_FILE)

        job_id = create_fine_tuning_job(
            training_file_id=training_file_id,
            validation_file_id=validation_file_id
        )

        final_job = monitor_job(job_id)

    except PermissionDeniedError as e:
        print("\n[ERROR] Fine-tuning is not available for your OpenAI organization.")
        print("[DETAIL] Your data upload worked, but OpenAI blocked the training job creation.")
        print("[DETAIL] This is an account/platform permission issue, not a Python code issue.")
        print("[DETAIL] You can still continue with a prompt-based classifier using the base model.\n")
        save_fallback_config()

    except Exception as e:
        print("\n[ERROR] Unexpected error:")
        print(type(e).__name__)
        print(e)
''', encoding="utf-8")

print("train.py created successfully.")
