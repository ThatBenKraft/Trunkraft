"""
Used for sending gmails and texts.
"""

import email
import imaplib
import smtplib
from email.message import EmailMessage
from pathlib import Path

# Defines email parameters
DEFAULT_SENDER_EMAIL = "kraft.scripting@gmail.com"
PASSWORD_PATH = Path(__file__).parent / "email_password.txt"
try:
    with open(PASSWORD_PATH, "r") as file:
        DEFAULT_SENDER_PASSWORD = file.readline()
except Exception as error:
    print(f"Error reading password: {error}")

# SMTP server configuration (for Gmail)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587  # For starttls

DEFAULT_NUMBER = 6102178448
DEFAULT_CARRIER = "verizon"
DEFAULT_RESPONSE_ADDRESS = str(DEFAULT_NUMBER) + "@vzwpix.com"

CARRIER_DOMAINS = {
    "verizon": "@vtext.com",
    "at&t": "@txt.att.net",
    "comcast": "@comcastpcs.textmsg.com",
    "edge": "@sms.edgewireless.com",
    "tmobil": "@tmomail.net",
}


def number_to_email(number: int, carrier: str) -> str:
    """
    Acquires text-to-email address from list of carrier domains.
    """
    return str(number) + CARRIER_DOMAINS[carrier]


DEFAULT_RECIPIENT = number_to_email(DEFAULT_NUMBER, DEFAULT_CARRIER)


class GmailClient:
    def __init__(
        self, sender_email=DEFAULT_SENDER_EMAIL, sender_password=DEFAULT_SENDER_PASSWORD
    ):
        # Sets members
        self.sender_email = sender_email
        # Initializes SMTP connection
        print("\nLogging in to SMTP and IMAP servers...")
        self.smtp_connection = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        self.smtp_connection.starttls()
        self.smtp_connection.login(self.sender_email, sender_password)
        # Initializes IMAP connection
        self.imap_connection = imaplib.IMAP4_SSL(SMTP_SERVER)
        self.imap_connection.login(self.sender_email, sender_password)
        print("Connected to email servers.")

    def send_email(
        self,
        subject: str,
        body: str,
        recipient: str = DEFAULT_RECIPIENT,
    ):
        # Composes email contents
        message = EmailMessage()
        message["From"] = self.sender_email
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)
        # Sends email
        self.smtp_connection.send_message(message)

    def send_text(
        self, message: str, number: int = DEFAULT_NUMBER, carrier: str = DEFAULT_CARRIER
    ):
        """
        Sends a text with specified message to number with carrier.
        """
        self.send_email("", message, number_to_email(number, carrier))
        print(f"Text [ {message} ] sent successfully.")

    def get_email(self, sender_email: str = DEFAULT_RESPONSE_ADDRESS, unread=False):

        print("\nAccessing inbox...")
        self.imap_connection.select("inbox")
        new_messages: list[EmailMessage] = []
        # Gets unread messages
        if unread:
            status_type, message_numbers = self.imap_connection.search(
                None, "UNSEEN", "FROM", f'"{sender_email}"'
            )
        else:
            status_type, message_numbers = self.imap_connection.search(
                None, "FROM", f'"{sender_email}"'
            )
        # If status is clear:
        if status_type == "OK":
            # Cleans message numebrs
            message_numbers = message_numbers[0].split()
            # For each message number:
            for number in message_numbers:
                # Fetches message data of corresponding email
                status_type, message_data = self.imap_connection.fetch(
                    number, "(RFC822)"
                )
                # If status is clear:
                if status_type == "OK":
                    # For each part of message data:
                    for response_part in message_data:
                        # If part is a tuple
                        if isinstance(response_part, tuple):
                            # Gets message from response part and adds to list
                            message: EmailMessage = email.message_from_bytes(response_part[1])  # type: ignore
                            new_messages.append(message)
        # Returns new messages
        return new_messages

    def read_text_attachment(self, message: EmailMessage) -> str:
        """
        Gets first line of text file attachment.
        """
        # I... don't even know
        for part in message.walk():
            if (
                part.get_content_maintype() != "multipart"
                and part.get("Content-Disposition") is not None
            ):
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if isinstance(payload, bytes):
                        payload = payload.decode(part.get_content_charset() or "utf-8")
                    return payload.splitlines()[0]  # type: ignore
                else:
                    print(f"Skipped non-text attachments: {part.get_filename()}")
        return ""

    def close(self):
        print("Closing Gmail client.")
        self.smtp_connection.quit()
        self.imap_connection.logout()

    def __exit__(self):
        self.close()


if __name__ == "__main__":

    client = GmailClient()
    # Sends text to default recipient
    message = input("\nEnter message: ")
    client.send_text(message)
    messages = client.get_email(unread=False)

    for message in messages[-5:]:
        print(client.read_text_attachment(message))
