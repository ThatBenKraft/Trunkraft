import smtplib
from email.message import EmailMessage
from pathlib import Path

# Defines email parameters
SENDER_EMAIL = "kraft.scripting@gmail.com"
PASSWORD_PATH = Path(__file__).parent / "email_password.txt"
with open(PASSWORD_PATH, "r") as file:
    SENDER_PASSWORD = file.readline()
DEFAULT_RECIPIENT = "6102178448@vtext.com"

# SMTP server configuration (for Gmail)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587  # For starttls


def send_text(player: str) -> None:
    """
    Sends a text about specified player joining the server.
    """
    send_email(subject="", body=f"{player} joined Trunkraft")
    print("Email sent successfully.")


def send_email(subject: str, body: str, recipient: str = DEFAULT_RECIPIENT) -> None:
    """
    Composes and sends email through Gmail smtp.
    """
    # Composes email contents
    message = EmailMessage()
    message["From"] = SENDER_EMAIL
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    # Opening an SMTP server:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        # Upgrades the connection to a secure TLS connection
        server.starttls()
        # Logs in with app password
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        # Sends the message
        server.send_message(message)


if __name__ == "__main__":
    # Sends custom email to default recipient
    subject = input("Enter subject: ")
    body = input("Enter body: ")
    send_email(DEFAULT_RECIPIENT, subject, body)
