%%writefile fine-tuning-ticket-classifier/train.py
from openai import OpenAI
from dotenv import load_dotenv
import time
from pathlib import Path

load_dotenv()

client = OpenAI()

BASE_MODEL = "gpt-4.1-nano-2025-04-14"


def upload_file(path: str):
    uploaded_file = client.files.create(
        file=open(path, "rb"),
        purpose="fine-tune"
    )

    print(f"Uploaded {path}")
    print(f"File ID: {uploaded_file.id}")

    return uploaded_file.id


def create_fine_tuning_job(training_file_id: str, validation_file_id: str):
    job = client.fine_tuning.jobs.create(
        model=BASE_MODEL,
        training_file=training_file_id,
        validation_file=validation_file_id,
        suffix="cyber-ticket-classifier"
    )

    print("Fine-tuning job created.")
    print(f"Job ID: {job.id}")

    Path("job_id.txt").write_text(job.id, encoding="utf-8")

    return job.id


def monitor_job(job_id: str):
    while True:
        job = client.fine_tuning.jobs.retrieve(job_id)

        print(f"Status: {job.status}")

        if job.status in ["succeeded", "failed", "cancelled"]:
            print("Final status:", job.status)
            print("Fine-tuned model:", job.fine_tuned_model)

            if job.fine_tuned_model:
                Path("fine_tuned_model.txt").write_text(
                    job.fine_tuned_model,
                    encoding="utf-8"
                )
                print("Fine-tuned model saved in fine_tuned_model.txt")

            return job

        time.sleep(30)


if __name__ == "__main__":
    training_file_id = upload_file("data/train.jsonl")
    validation_file_id = upload_file("data/validation.jsonl")

    job_id = create_fine_tuning_job(
        training_file_id=training_file_id,
        validation_file_id=validation_file_id
    )

    final_job = monitor_job(job_id)
