# Open-Source Cybersecurity Ticket Classifier

A practical, open-source machine learning project for classifying cybersecurity support tickets using **Google Colab**, **Hugging Face Transformers**, **DistilBERT**, and **FastAPI**.

This project fine-tunes a lightweight transformer model to classify cybersecurity tickets into predefined operational security categories such as phishing, vulnerability management, logging and monitoring, identity access management, cloud security, and incident response.

The model predicts the ticket category, while a deterministic business rule layer adds the priority and recommended action. This keeps the output controlled, explainable, and suitable for a beginner-friendly AI architecture demonstration.

---

## 1. Project Overview

Cybersecurity teams receive many operational tickets every day. These tickets may relate to phishing alerts, failed backups, vulnerability findings, SIEM logging issues, privileged access events, DLP alerts, network security requests, or audit evidence requests.

Manually classifying these tickets can be repetitive and time-consuming. This project demonstrates how a small open-source model can be fine-tuned to automatically classify cybersecurity tickets and return a structured JSON response.

### Example Input

```text
The SIEM stopped receiving logs from the firewall.
```

### Example Output

```json
{
  "category": "logging_monitoring",
  "confidence": 0.93,
  "priority": "high",
  "recommended_action": "Check log forwarding, connector health, network connectivity, parsing rules, and SIEM ingestion status."
}
```

---

## 2. Why This Project Does Not Use OpenAI Fine-Tuning

This project uses a fully open-source fine-tuning approach instead of OpenAI fine-tuning.

The selected stack is:

```text
Google Colab
+ Hugging Face Transformers
+ DistilBERT
+ FastAPI
+ Optional Hugging Face Spaces deployment
```

This approach is suitable because it is:

* Free to run in Google Colab for experimentation.
* Based on open-source models and libraries.
* Easy to explain for beginners.
* Lightweight enough for a practical demo.
* Deployable through a local API or a simple cloud demo.

---

## 3. Architecture

The architecture has two main phases:

```text
1. Training Phase
2. Deployment and Inference Phase
```

### 3.1 Training Phase

```text
Cybersecurity ticket dataset
        ↓
Preprocessing and label encoding
        ↓
DistilBERT tokenizer
        ↓
Fine-tuned DistilBERT classifier
        ↓
Evaluation
        ↓
Saved model artifacts
```

During training, the model learns how to map ticket text to a cybersecurity category.

Example:

```text
Input ticket:
"A user reported a suspicious email asking them to reset their password."

Target label:
phishing
```

The model is trained only to predict the category. It does not generate free-text recommendations.

---

### 3.2 Deployment and Inference Phase

```text
User ticket
        ↓
FastAPI endpoint
        ↓
Fine-tuned DistilBERT classifier
        ↓
Predicted category
        ↓
Business rule layer
        ↓
Structured JSON response
```

The business rule layer maps each predicted category to:

* A priority.
* A recommended action.

This makes the response more reliable and easier to control.

---

## 4. Categories Supported

The classifier supports the following cybersecurity ticket categories:

| Category                       | Meaning                                                             |
| ------------------------------ | ------------------------------------------------------------------- |
| `logging_monitoring`           | SIEM, log forwarding, log collector, parser, or monitoring issues   |
| `phishing`                     | Suspicious emails, malicious links, credential theft attempts       |
| `vulnerability_management`     | Vulnerability scans, CVEs, patching, remediation tracking           |
| `backup_recovery`              | Backup failures, restore issues, recovery point problems            |
| `identity_access_management`   | User access, approvals, inactive accounts, excessive privileges     |
| `privileged_access_management` | PAM sessions, privileged accounts, password rotation, recordings    |
| `data_protection`              | DLP alerts, sensitive data exposure, unauthorized sharing           |
| `network_security`             | Firewall rules, VPN, segmentation, exposed ports                    |
| `endpoint_security`            | EDR, antivirus, workstation protection, endpoint alerts             |
| `cloud_security`               | Cloud IAM, storage exposure, encryption, audit logging              |
| `incident_response`            | Possible compromise, suspicious activity, brute force, exfiltration |
| `compliance_audit`             | Audit evidence, policy exceptions, control documentation            |

---

## 5. Technology Stack

| Component                 | Purpose                       |
| ------------------------- | ----------------------------- |
| Python                    | Main programming language     |
| Google Colab              | Free training environment     |
| Hugging Face Transformers | Model and tokenizer library   |
| Hugging Face Datasets     | Dataset preparation           |
| DistilBERT                | Lightweight transformer model |
| PyTorch                   | Deep learning backend         |
| Scikit-learn              | Evaluation metrics            |
| FastAPI                   | API deployment                |
| Uvicorn                   | ASGI server for FastAPI       |
| Pydantic                  | Request validation            |

---

## 6. Project Structure

```text
fine-tuning-ticket-classifier/
│
├── data/
│   ├── train.jsonl
│   └── validation.jsonl
│
├── ticket_classifier_model/
│   ├── config.json
│   ├── model.safetensors
│   ├── tokenizer.json
│   ├── tokenizer_config.json
│   ├── special_tokens_map.json
│   └── label_mappings.json
│
├── app.py
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 7. Installation

### 7.1 Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install transformers datasets accelerate scikit-learn fastapi uvicorn pydantic torch python-multipart
```

---

## 8. Training in Google Colab

### Step 1 — Install Libraries

```python
!pip install -q transformers datasets accelerate scikit-learn fastapi uvicorn pydantic python-multipart
```

### Step 2 — Train the Model

Run the notebook cells that:

1. Create the cybersecurity ticket dataset.
2. Encode the labels.
3. Load `distilbert-base-uncased`.
4. Tokenize the text.
5. Fine-tune the model using Hugging Face `Trainer`.
6. Evaluate the model.
7. Save the trained model into:

```text
ticket_classifier_model/
```

---

## 9. Model Training Logic

The model receives a ticket text and predicts one category.

Example:

```text
Ticket:
"A critical vulnerability was detected on an internet-facing server."

Predicted category:
vulnerability_management
```

The training process uses:

* Tokenization.
* Supervised classification.
* Cross-entropy loss.
* Evaluation with accuracy, precision, recall, and F1-score.

---

## 10. Evaluation Metrics

The model is evaluated using:

| Metric    | Description                               |
| --------- | ----------------------------------------- |
| Accuracy  | Percentage of correct predictions         |
| Precision | How many predicted labels were correct    |
| Recall    | How many true labels were correctly found |
| F1-score  | Balance between precision and recall      |

Example evaluation output:

```json
{
  "eval_loss": 0.42,
  "eval_accuracy": 0.91,
  "eval_precision": 0.92,
  "eval_recall": 0.91,
  "eval_f1": 0.90
}
```

The exact result depends on the dataset size, data quality, model settings, and training environment.

---

## 11. Important Note About Dataset Size

The starter dataset is designed for learning and demonstration.

For a more serious model, the dataset should be expanded to include:

* At least several hundred examples.
* Balanced examples across all categories.
* Realistic ticket wording.
* Anonymized production-like data.
* Clear and consistent labels.
* A separate validation and test set.

A small dataset is useful for demonstration, but it is not enough for production-level reliability.

---

## 12. Prediction Logic

The model predicts only the category.

The final JSON response is created by combining:

```text
Model prediction
+ Confidence score
+ ACTION_MAP business rules
```

Example:

```python
ACTION_MAP = {
    "phishing": {
        "priority": "high",
        "recommended_action": "Collect the email header, block malicious indicators, reset credentials if needed, revoke sessions, and investigate possible compromise."
    }
}
```

This design is intentional.

It avoids relying on the classifier to generate uncontrolled recommendations. Instead, the model performs classification, and the rule layer provides consistent operational guidance.

---

## 13. Running the API Locally

After training and saving the model, run:

```bash
uvicorn app:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

FastAPI will provide an interactive Swagger interface.

---

## 14. API Usage

### Endpoint

```http
POST /classify
```

### Request Body

```json
{
  "ticket": "The SIEM stopped receiving logs from the firewall."
}
```

### Response Body

```json
{
  "input": "The SIEM stopped receiving logs from the firewall.",
  "category": "logging_monitoring",
  "confidence": 0.93,
  "priority": "high",
  "recommended_action": "Check log forwarding, connector health, network connectivity, parsing rules, and SIEM ingestion status."
}
```

---

## 15. FastAPI Application

The API performs the following steps:

```text
Receive ticket
        ↓
Validate request with Pydantic
        ↓
Run DistilBERT classifier
        ↓
Extract predicted category and confidence
        ↓
Apply ACTION_MAP
        ↓
Return JSON response
```

---

## 16. Deployment Option: Hugging Face Spaces

This project can be deployed as a small demo API on Hugging Face Spaces using Docker.

Required files:

```text
app.py
requirements.txt
Dockerfile
ticket_classifier_model/
```

The Space should be created using the Docker SDK option.

The API will run with:

```bash
uvicorn app:app --host 0.0.0.0 --port 7860
```

---

## 17. Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
```

---

## 18. Example End-to-End Flow

```text
User enters ticket:
"The backup job failed last night for the production database."

Model predicts:
backup_recovery

Business rule layer adds:
priority = high
recommended_action = Review backup logs, identify the failure cause, rerun backup if possible, and confirm restore point availability.

Final API response:
{
  "category": "backup_recovery",
  "confidence": 0.94,
  "priority": "high",
  "recommended_action": "Review backup logs, identify the failure cause, rerun backup if possible, and confirm restore point availability."
}
```

---

## 19. Security and Privacy Considerations

Do not train the model on raw confidential tickets without approval.

Before using real tickets:

* Remove personal data.
* Remove secrets and credentials.
* Remove customer-sensitive information.
* Remove IP addresses if not required.
* Remove emails, names, phone numbers, and identifiers.
* Validate that the dataset is authorized for machine learning use.
* Keep a documented data handling process.

This project should be treated as a learning and demonstration system unless it is properly validated and approved for production use.

---

## 20. Limitations

This project has several limitations:

1. The starter dataset is small.
2. The model may misclassify ambiguous tickets.
3. Similar categories may be confused, such as incident response and endpoint security.
4. Confidence scores should not be treated as absolute truth.
5. The recommended action is rule-based and generic.
6. Real production deployment requires stronger validation, monitoring, and governance.

---

## 21. Recommended Improvements

Future improvements may include:

* Expanding the dataset to 500+ examples.
* Adding real anonymized tickets.
* Creating a separate test set.
* Adding confusion matrix analysis.
* Adding model versioning.
* Adding feedback collection from analysts.
* Adding active learning.
* Adding multilingual support.
* Adding severity prediction as a second model.
* Adding integration with Jira, ServiceNow, or a SIEM platform.
* Deploying with authentication and audit logging.

---

## 22. Why DistilBERT?

DistilBERT is a lightweight transformer model that is smaller and faster than BERT while remaining strong for text classification tasks.

It is a good choice for this project because:

* It is simple to fine-tune.
* It runs well in Google Colab.
* It is suitable for short text classification.
* It is easier to deploy than larger language models.
* It provides a clean learning path for beginners.

---

## 23. Production Readiness Checklist

Before using this system in production, validate the following:

* [ ] Dataset is approved and anonymized.
* [ ] Labels are reviewed by cybersecurity experts.
* [ ] Training, validation, and test sets are separated.
* [ ] Evaluation metrics are acceptable.
* [ ] Confusion matrix is reviewed.
* [ ] False positives and false negatives are analyzed.
* [ ] API is protected with authentication.
* [ ] Logs are monitored.
* [ ] Model version is tracked.
* [ ] Business rules are approved.
* [ ] Human review is kept for high-risk cases.

---

## 24. Educational Purpose

This project is designed as a practical AI engineering exercise for cybersecurity ticket classification.

It demonstrates:

* How to prepare labeled text data.
* How to fine-tune an open-source transformer model.
* How to evaluate a classifier.
* How to save and reuse a model.
* How to expose the model through an API.
* How to combine machine learning with deterministic business rules.

---

## 25. Final Summary

This project provides a complete open-source alternative to OpenAI fine-tuning for cybersecurity ticket classification.

The final system follows a clean and explainable design:

```text
DistilBERT predicts the category.
Business rules add priority and recommended action.
FastAPI exposes the result as a JSON API.
```

This makes the solution practical, transparent, and easy to demonstrate.
