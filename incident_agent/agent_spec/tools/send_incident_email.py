from __future__ import annotations

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ibm_watsonx_orchestrate.agent_builder.tools import ToolPermission, tool


DEFAULT_ENGINEER_EMAIL = ""
SENDER_EMAIL = "mitpatel.ce@gmail.com"
SENDER_PASSWORD = ""
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USE_TLS = True


@tool(permission=ToolPermission.READ_WRITE)
def send_incident_email(
    service: str,
    environment: str,
    severity: str,
    summary: str,
    recommended_actions: str,
    email_subject: str = "",
    email_body: str = "",
    recipient_email: str = "",
) -> str:
    """
    Send incident notification email to the on-call engineer.
    The agent can provide custom email_subject and email_body.
    """
    default_subject = f"[{severity}] Incident - {service} ({environment})"
    default_body = (
        f"Service: {service}\n"
        f"Environment: {environment}\n"
        f"Severity: {severity}\n"
        f"Summary: {summary}\n\n"
        f"Recommended Actions:\n{recommended_actions}\n"
    )
    subject = email_subject.strip() if email_subject and email_subject.strip() else default_subject
    body = email_body.strip() if email_body and email_body.strip() else default_body

    recipient = recipient_email.strip() if recipient_email and recipient_email.strip() else DEFAULT_ENGINEER_EMAIL

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            if SMTP_USE_TLS:
                server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient, msg.as_string())
    except Exception as exc:
        return f"email_failed: {exc}"

    return f"email_sent: {recipient}"
