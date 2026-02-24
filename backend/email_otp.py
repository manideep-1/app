"""
Email OTP for signup: send OTP via SMTP (or log to console if not configured).
"""
import os
import random
import string
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

logger = logging.getLogger(__name__)

OTP_LENGTH = 6
OTP_EXPIRE_MINUTES = 10


def _generate_otp() -> str:
    return "".join(random.choices(string.digits, k=OTP_LENGTH))


def _smtp_configured() -> bool:
    return bool(
        os.environ.get("SMTP_HOST")
        and os.environ.get("SMTP_PORT")
        and os.environ.get("MAIL_FROM")
    )


def send_otp_email(to_email: str, otp: str) -> None:
    """Send OTP to the given email. If SMTP is not configured, log OTP to console."""
    app_name = os.environ.get("APP_NAME", "ifelse")
    subject = f"Your {app_name} verification code"
    body = f"""Your verification code is: {otp}

This code expires in {OTP_EXPIRE_MINUTES} minutes. If you didn't request this, you can ignore this email.
"""
    if _smtp_configured():
        try:
            msg = MIMEMultipart()
            msg["Subject"] = subject
            msg["From"] = os.environ["MAIL_FROM"]
            msg["To"] = to_email
            msg.attach(MIMEText(body, "plain"))
            with smtplib.SMTP(
                os.environ["SMTP_HOST"],
                int(os.environ.get("SMTP_PORT", "587")),
                timeout=10,
            ) as server:
                if os.environ.get("SMTP_USE_TLS", "true").lower() == "true":
                    server.starttls()
                if os.environ.get("SMTP_USER"):
                    server.login(
                        os.environ["SMTP_USER"],
                        os.environ.get("SMTP_PASSWORD", ""),
                    )
                server.sendmail(os.environ["MAIL_FROM"], [to_email], msg.as_string())
            logger.info("OTP email sent to %s", to_email)
        except Exception as e:
            logger.exception("Failed to send OTP email: %s", e)
            raise RuntimeError("Failed to send verification email. Please try again later.") from e
    else:
        logger.warning("SMTP not configured. OTP for %s: %s", to_email, otp)


def get_otp_expire_minutes() -> int:
    return OTP_EXPIRE_MINUTES


def generate_otp() -> str:
    return _generate_otp()
