from pathlib import Path
import json

# Detect project folder
project_name = "fine-tuning-ticket-classifier"
current = Path.cwd()

if current.name == project_name:
    project = Path(".")
else:
    project = Path(project_name)

data_dir = project / "data"
data_dir.mkdir(parents=True, exist_ok=True)

system_prompt = (
    "You classify cybersecurity tickets. "
    "Always return valid JSON with category, priority, and recommended_action."
)

# ============================================================
# Bigger training dataset
# ============================================================

train_examples = [
    # Logging and monitoring
    ("The SIEM stopped receiving logs from the firewall.",
     "logging_monitoring", "high",
     "Check firewall log forwarding, connector health, network connectivity, and SIEM ingestion status."),

    ("QRadar is not receiving authentication logs from Active Directory.",
     "logging_monitoring", "high",
     "Verify the log source configuration, agent status, network connectivity, and parsing errors in the SIEM."),

    ("Several Linux servers stopped sending syslog events after a reboot.",
     "logging_monitoring", "medium",
     "Check syslog service status, forwarding configuration, firewall rules, and SIEM ingestion health."),

    ("The SOC dashboard shows no events from the proxy since yesterday.",
     "logging_monitoring", "high",
     "Validate proxy logging, collector availability, network reachability, and SIEM ingestion status."),

    ("A log collector disk is almost full and may stop ingesting events.",
     "logging_monitoring", "high",
     "Free disk space, archive old logs, check retention settings, and confirm event ingestion is restored."),

    # Phishing
    ("A user reported a suspicious email asking them to reset their password.",
     "phishing", "medium",
     "Collect the email header, block malicious indicators, alert users, and verify whether credentials were submitted."),

    ("A user clicked a suspicious link received by email.",
     "phishing", "high",
     "Reset the user's password if needed, review authentication logs, block the URL, and investigate possible compromise."),

    ("Multiple employees received the same email with a suspicious attachment.",
     "phishing", "high",
     "Collect samples, quarantine the email, block indicators, scan endpoints, and notify affected users."),

    ("An email impersonating the CEO requested urgent payment.",
     "phishing", "high",
     "Preserve the email, block sender indicators, alert finance users, and validate whether any payment was initiated."),

    ("A user entered credentials on a fake login page.",
     "phishing", "critical",
     "Reset credentials, revoke active sessions, review authentication logs, and investigate account compromise."),

    # Vulnerability management
    ("A critical vulnerability was detected on an internet-facing server.",
     "vulnerability_management", "critical",
     "Validate exposure, assign a remediation owner, apply patch or mitigation, and perform a rescan after remediation."),

    ("The vulnerability scan did not cover several production servers.",
     "vulnerability_management", "medium",
     "Identify missing assets, verify scanner reachability and credentials, update scan scope, and rerun the scan."),

    ("A high-risk CVE is still open after the remediation SLA.",
     "vulnerability_management", "high",
     "Escalate to the asset owner, validate remediation blockers, define a corrective action plan, and track closure."),

    ("An authenticated scan failed because the scanner credentials are invalid.",
     "vulnerability_management", "medium",
     "Update scanner credentials, test authentication, rerun the scan, and confirm authenticated coverage."),

    ("A vulnerability previously marked as remediated appeared again in the latest scan.",
     "vulnerability_management", "high",
     "Investigate recurrence, validate patch persistence, perform root cause analysis, and update remediation evidence."),

    # Backup and recovery
    ("The backup job failed last night for the production database.",
     "backup_recovery", "high",
     "Review backup logs, identify the failure cause, rerun the backup if possible, and confirm restore point availability."),

    ("The backup repository is almost full.",
     "backup_recovery", "high",
     "Check storage capacity, apply retention policies, clean obsolete backups, and verify future backup execution."),

    ("A restore test failed for a critical application.",
     "backup_recovery", "critical",
     "Analyze restore logs, validate backup integrity, identify the failure point, and repeat the restore test."),

    ("Daily backups are taking longer than the approved backup window.",
     "backup_recovery", "medium",
     "Review backup performance, optimize schedules, check network throughput, and adjust backup policies if required."),

    ("A production server has not been backed up for three days.",
     "backup_recovery", "high",
     "Check backup agent status, validate policy assignment, rerun backup, and confirm recovery point availability."),

    # IAM
    ("An administrator account was created without approval evidence.",
     "identity_access_management", "high",
     "Verify the request and approval trail, suspend unauthorized access if required, and document the exception."),

    ("Several inactive users still have access to a critical application.",
     "identity_access_management", "high",
     "Review user status, revoke unnecessary access, notify application owners, and update access review evidence."),

    ("A user still has access after leaving the company.",
     "identity_access_management", "critical",
     "Disable the account immediately, review recent activity, notify the owner, and investigate offboarding failure."),

    ("A manager requested access for a new employee to the finance application.",
     "identity_access_management", "medium",
     "Validate business need, obtain required approvals, assign least-privilege access, and document the request."),

    ("A user has excessive privileges compared to their job role.",
     "identity_access_management", "high",
     "Review role assignment, validate business justification, remove unnecessary privileges, and update access records."),

    # PAM
    ("PAM session recording is not working for Unix servers.",
     "privileged_access_management", "high",
     "Check PAM connector status, recording configuration, storage availability, and perform a controlled access test."),

    ("An admin account was used outside approved maintenance hours.",
     "privileged_access_management", "high",
     "Review PAM logs, validate the activity with the account owner, and escalate if the access was unauthorized."),

    ("A privileged account password rotation failed.",
     "privileged_access_management", "high",
     "Check PAM rotation policy, validate target connectivity, review error logs, and manually secure the credential if needed."),

    ("A shared administrator account is being used without individual accountability.",
     "privileged_access_management", "high",
     "Move access through PAM, enforce named-user accountability, enable session recording, and remove direct shared access."),

    ("A privileged session was opened without a valid ticket reference.",
     "privileged_access_management", "medium",
     "Validate the session purpose, request missing justification, update evidence, and reinforce access control procedures."),

    # DLP and data protection
    ("A DLP alert indicates that sensitive data was sent to a personal email address.",
     "data_protection", "high",
     "Review the DLP event, identify the data type, contact the user manager, and assess whether incident escalation is required."),

    ("A user uploaded confidential files to an unauthorized cloud storage service.",
     "data_protection", "high",
     "Identify exposed files, block unauthorized storage access, contact the user, and assess data leakage impact."),

    ("Sensitive customer data was found in an unencrypted spreadsheet.",
     "data_protection", "high",
     "Secure the file, apply encryption, restrict access, and remind the owner of data handling requirements."),

    ("A database export containing personal data was shared with an external recipient.",
     "data_protection", "critical",
     "Contain the exposure, identify recipients, assess regulatory impact, notify stakeholders, and initiate incident handling."),

    ("A DLP rule is generating too many false positives.",
     "data_protection", "medium",
     "Review detection logic, tune the rule, validate sample alerts, and monitor effectiveness after adjustment."),

    # Network security
    ("A firewall rule change was requested without business justification.",
     "network_security", "medium",
     "Request business justification, validate source and destination, assess risk, and require formal approval before implementation."),

    ("A new inbound rule exposes an internal server to the internet.",
     "network_security", "critical",
     "Validate the business need, restrict exposure, apply compensating controls, and obtain security approval."),

    ("VPN users cannot access a production subnet.",
     "network_security", "high",
     "Check VPN routing, firewall rules, network ACLs, and confirm access with a controlled test."),

    ("An unauthorized open port was detected on a public IP address.",
     "network_security", "high",
     "Validate the service owner, close unnecessary exposure, review firewall rules, and rescan the asset."),

    ("A network segmentation rule is blocking communication between approved servers.",
     "network_security", "medium",
     "Review segmentation policy, validate traffic flow requirements, adjust rules, and test connectivity."),

    # Endpoint security
    ("An endpoint security agent is disabled on a user workstation.",
     "endpoint_security", "high",
     "Re-enable the agent, check tamper protection, scan the endpoint, and investigate why protection was disabled."),

    ("Malware was detected and quarantined on a laptop.",
     "endpoint_security", "high",
     "Review detection details, run a full scan, confirm quarantine status, and investigate possible infection vector."),

    ("Several workstations have outdated antivirus signatures.",
     "endpoint_security", "medium",
     "Force signature update, check update policy, validate endpoint connectivity, and monitor compliance."),

    ("A laptop has not checked in to the endpoint management platform for two weeks.",
     "endpoint_security", "medium",
     "Confirm device status, contact the user, verify agent health, and update asset inventory if needed."),

    ("EDR generated an alert for suspicious PowerShell activity.",
     "endpoint_security", "high",
     "Collect process details, isolate endpoint if needed, review user activity, and investigate possible compromise."),

    # Cloud security
    ("An S3 bucket was detected as publicly accessible.",
     "cloud_security", "critical",
     "Restrict public access, review bucket policy, identify exposed data, and assess whether incident escalation is required."),

    ("A cloud admin role was assigned without approval.",
     "cloud_security", "high",
     "Validate approval evidence, remove excessive permissions, review activity logs, and update IAM records."),

    ("A security group allows SSH access from the internet.",
     "cloud_security", "high",
     "Restrict SSH access, apply trusted source ranges, validate business justification, and monitor exposure."),

    ("Cloud audit logging is disabled in one production account.",
     "cloud_security", "critical",
     "Enable audit logging, verify log delivery, investigate the disablement, and review activity during the logging gap."),

    ("A cloud workload is missing required encryption at rest.",
     "cloud_security", "high",
     "Enable encryption, validate key management settings, assess data sensitivity, and document remediation evidence."),

    # Incident response
    ("A server is showing signs of possible compromise.",
     "incident_response", "critical",
     "Isolate the server if needed, collect evidence, analyze indicators, notify stakeholders, and initiate incident response procedures."),

    ("Unusual outbound traffic was detected from a production server.",
     "incident_response", "critical",
     "Contain the server, review network logs, identify destination indicators, and investigate potential data exfiltration."),

    ("A user reported that their account performed actions they did not initiate.",
     "incident_response", "high",
     "Reset credentials, revoke sessions, review account activity, and investigate possible compromise."),

    ("A security alert indicates brute-force attempts against a VPN portal.",
     "incident_response", "high",
     "Review authentication logs, block malicious sources, enforce MFA, and monitor for successful unauthorized access."),

    ("A suspicious scheduled task was found on a Windows server.",
     "incident_response", "high",
     "Collect task details, review recent changes, scan the server, and investigate persistence indicators."),

    # Compliance and audit
    ("The auditor requested evidence of quarterly access reviews.",
     "compliance_audit", "medium",
     "Collect access review reports, approvals, remediation evidence, and provide the audit trail."),

    ("PCI DSS evidence is missing for vulnerability remediation.",
     "compliance_audit", "high",
     "Gather scan results, remediation tickets, closure evidence, and rescan confirmation for the PCI scope."),

    ("An ISO 27001 control owner did not provide evidence before the deadline.",
     "compliance_audit", "medium",
     "Follow up with the control owner, document delay reason, and escalate if evidence remains unavailable."),

    ("A policy exception expired but the risk is still open.",
     "compliance_audit", "high",
     "Review the exception status, obtain renewal approval or remediation plan, and update the risk register."),

    ("An audit finding remains open after the committed closure date.",
     "compliance_audit", "high",
     "Escalate to the action owner, update the remediation plan, and provide revised closure evidence."),
]

# ============================================================
# Validation dataset
# ============================================================

validation_examples = [
    ("A user entered credentials on a fake login page.",
     "phishing", "high",
     "Reset the user's password, revoke active sessions, review authentication logs, and investigate possible account compromise."),

    ("A production server has not been scanned for vulnerabilities this month.",
     "vulnerability_management", "medium",
     "Verify asset inventory, update scan coverage, check scanner reachability, and schedule a new authenticated scan."),

    ("An admin account was used outside approved maintenance hours.",
     "privileged_access_management", "high",
     "Review PAM logs, validate the activity with the account owner, and escalate if the access was unauthorized."),

    ("The SIEM parser is failing for proxy logs.",
     "logging_monitoring", "medium",
     "Review parser errors, validate log format changes, update parsing rules, and confirm dashboard visibility."),

    ("A backup completed successfully but the restore test was not performed.",
     "backup_recovery", "medium",
     "Schedule a restore test, validate backup integrity, document results, and update recovery evidence."),

    ("An employee changed role but kept access to the previous department application.",
     "identity_access_management", "high",
     "Review role change records, remove unnecessary access, notify the application owner, and update access evidence."),

    ("A DLP alert shows confidential data copied to a USB device.",
     "data_protection", "high",
     "Review the DLP event, identify copied data, contact the user manager, and escalate if data leakage is confirmed."),

    ("A firewall rule allows traffic from any source to a sensitive database.",
     "network_security", "critical",
     "Restrict the rule, validate required sources, assess exposure, and obtain formal security approval."),

    ("An EDR alert detected suspicious command execution on a workstation.",
     "endpoint_security", "high",
     "Analyze the command, isolate the device if needed, run endpoint scans, and investigate compromise indicators."),

    ("A cloud storage bucket contains sensitive files without encryption.",
     "cloud_security", "high",
     "Enable encryption, review access permissions, assess data sensitivity, and document remediation evidence."),

    ("Multiple failed login attempts were detected against a privileged account.",
     "incident_response", "high",
     "Review authentication logs, block suspicious sources, validate account status, and investigate possible attack activity."),

    ("The auditor requested proof that firewall changes are formally approved.",
     "compliance_audit", "medium",
     "Collect change tickets, approval evidence, risk assessments, and implementation records for the audit request."),

    ("A database server stopped sending logs after a maintenance activity.",
     "logging_monitoring", "high",
     "Check logging service status, verify forwarding configuration, review maintenance changes, and confirm SIEM ingestion."),

    ("A user reported receiving a fake invoice attachment.",
     "phishing", "medium",
     "Collect the email sample, scan the attachment, block malicious indicators, and warn potentially affected users."),

    ("An internet-facing server has an overdue critical patch.",
     "vulnerability_management", "critical",
     "Escalate remediation, apply patch or mitigation, verify exposure, and perform a post-remediation rescan."),
]

def make_record(ticket, category, priority, action):
    assistant_json = {
        "category": category,
        "priority": priority,
        "recommended_action": action
    }

    return {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": ticket},
            {"role": "assistant", "content": json.dumps(assistant_json)}
        ]
    }

def write_jsonl(path, examples):
    with open(path, "w", encoding="utf-8") as f:
        for ticket, category, priority, action in examples:
            record = make_record(ticket, category, priority, action)
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

train_path = data_dir / "train.jsonl"
validation_path = data_dir / "validation.jsonl"

write_jsonl(train_path, train_examples)
write_jsonl(validation_path, validation_examples)

print("Bigger dataset created successfully.")
print("Training examples:", len(train_examples))
print("Validation examples:", len(validation_examples))
print("Train file:", train_path.resolve())
print("Validation file:", validation_path.resolve())
