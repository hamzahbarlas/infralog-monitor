import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64

# Load environment variables
load_dotenv(Path(__file__).parent.parent / "config" / ".env")

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")

# ── Email Builder ─────────────────────────────────────────────

def send_alert(parsed_report, report_filepath, risk_score):
    critical = parsed_report.severity_counts.get("CRITICAL", 0)
    error = parsed_report.severity_counts.get("ERROR", 0)

    if risk_score >= 70:
        risk_label = "HIGH"
    elif risk_score >= 40:
        risk_label = "MEDIUM"
    else:
        risk_label = "LOW"

    subject = f"[{risk_label} RISK] InfraLog Alert - Score {risk_score}/100 - {parsed_report.source_file}"

    body = f"""
InfraLog Monitor - Automated Alert
===================================

Risk Score  : {risk_score}/100  ({risk_label} RISK)
Source File : {parsed_report.source_file}
Generated   : {parsed_report.parse_time}
Total Events: {parsed_report.total_events}

SEVERITY BREAKDOWN
------------------
CRITICAL : {critical}
ERROR    : {error}
WARNING  : {parsed_report.severity_counts.get("WARNING", 0)}
INFO     : {parsed_report.severity_counts.get("INFO", 0)}

INCIDENTS DETECTED
------------------
Brute Force Attempts : {len(parsed_report.brute_force_ips)}
Unauthorized Access  : {len(parsed_report.unauthorized_access)}
Off Hours Logins     : {len(parsed_report.off_hours_logins)}
Critical Resources   : {len(parsed_report.resource_critical)}
Service Crashes      : {len(parsed_report.service_crashes)}

Full report attached.

-- InfraLog Monitor
"""

    # Build the email
    message = Mail(
        from_email=EMAIL_FROM,
        to_emails=EMAIL_TO,
        subject=subject,
        plain_text_content=body
    )

    # Attach the report file
    with open(report_filepath, "rb") as f:
        report_data = f.read()

    encoded = base64.b64encode(report_data).decode()
    attachment = Attachment(
        FileContent(encoded),
        FileName(Path(report_filepath).name),
        FileType("text/plain"),
        Disposition("attachment")
    )
    message.attachment = attachment

    # Send
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return True, response.status_code
    except Exception as e:
        return False, str(e)


# ── Quick Test ───────────────────────────────────────────────

if __name__ == "__main__":
    sys.path.append(str(Path(__file__).parent.parent))
    from parser.log_parser import parse_log_file
    from reporter.report_builder import save_report

    logs = sorted(Path("logs/incoming").glob("*.log"))
    if not logs:
        print("No log files found. Run the generator first.")
        sys.exit(1)

    report = parse_log_file(logs[-1])
    filename, content = save_report(report)

    critical = report.severity_counts.get("CRITICAL", 0)
    error = report.severity_counts.get("ERROR", 0)
    risk_score = min(100, (critical * 3) + (error * 1))

    print(f"Sending test alert email - Risk Score: {risk_score}/100")
    success, result = send_alert(report, filename, risk_score)

    if success:
        print(f"Email sent successfully - Status: {result}")
    else:
        print(f"Email failed: {result}")