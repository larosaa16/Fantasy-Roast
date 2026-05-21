"""
Sends the assembled HTML email via Gmail SMTP.
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_roast_email(html: str, week: int, league_name: str) -> None:
    sender = os.environ["EMAIL_SENDER"]
    password = os.environ["EMAIL_PASSWORD"]
    recipients_raw = os.environ["EMAIL_RECIPIENTS"]
    recipients = [r.strip() for r in recipients_raw.split(",") if r.strip()]

    subject = f"&#x1F525; Week {week} Roast — {league_name}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipients, msg.as_string())

    print(f"Roast email sent to {len(recipients)} recipients.")
