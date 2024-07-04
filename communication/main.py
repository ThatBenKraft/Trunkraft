import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

import log_parser
from colors import Colors
from gmail import GmailClient
from registry import Registry

BASE_PATH = Path(__file__).parent
DATABASES_PATH = BASE_PATH / "databases/"
CHAT_LOG_PATH = DATABASES_PATH / "chat_log.json"
PENDING_MESSAGES_PATH = DATABASES_PATH / "pending_messages.json"

# List of players to not notify about
IGNORED_PLAYERS = ["Optica"]

TEXT_WIDTH = 60


def print_title(line: str, color: str = Colors.RED) -> None:
    print("\n" + f"{color}[[    {line}    ]]{Colors.RESET}".center(TEXT_WIDTH) + "\n")


def compile_message(player: str, message: str, timestamp: str = "") -> str:
    # If timestamp not specified:
    if not timestamp:
        # Gets UTC time
        utc_now = datetime.now(timezone.utc)
        # Creates timestamp to match log format
        timestamp = utc_now.strftime("[%H:%M:%S]")
    return f"[{timestamp}] <{player}> {message}"


def main():

    # Acquires log and function path from user
    log_path, message_function_path = log_parser.select_os_paths()
    # Creates Gmail client
    gmail_client = GmailClient()
    # Creates registries for online players and chat log
    online_players = Registry()
    chat_log = Registry(CHAT_LOG_PATH, max_length=100)
    pending_messages = Registry(PENDING_MESSAGES_PATH)

    # Asks for chat message notifications confirmation
    chat_confirmation = input(
        "\nWould you like to recieve chat notifications? (y/n): "
    ).upper()
    # If yes:
    chat_notifications = chat_confirmation != "" and chat_confirmation in "YES"

    try:
        # Begins looping
        loop_number = 0

        while True:
            print_title("MESSAGES FROM PHONE TO SERVER")
            print(f"Pending messages to be sent: {pending_messages}")
            # Removes any messages already in any part of chat log
            for compiled_message in pending_messages:
                if compiled_message in chat_log:
                    pending_messages.remove(compiled_message)

            # Gets unread emails
            unread_emails = gmail_client.get_email(unread=True)
            print(f"Unread emails: ", end="")
            # For each unread email:
            for email in unread_emails:
                # Gets message from attachment
                message = gmail_client.read_text_attachment(email)
                print(message, end=", ")
                # Adds details to message
                compiled_message = compile_message("Server", message)
                # Adds compiled message to pending deque
                if compiled_message not in pending_messages:
                    pending_messages.add(compiled_message)
            print("")

            ## WRITING NEW INCOMING MESSAGES TO MCFUNCTION
            # With function file:
            with open(message_function_path, "w") as function_file:
                # Writes reload header
                function_file.write("reload\n")
                # For email in list:
                print(f"Messages written to function file: ", end="")
                for message in pending_messages:
                    # Writes message as command
                    print(message, end=", ")
                    function_file.write(f"say {message}\n")
            print("")

            print_title("MESSAGES FROM SERVER TO PHONE")

            # Acquires logs from file
            logs = log_parser.get_logs(log_path)

            # Gets chat messages from logs
            chat_messages = log_parser.get_messages(logs)
            # For each chat message:
            for player, message, timestamp in chat_messages:
                # Continue to next message if in chat log
                timestamped_message = compile_message(player, message, timestamp)
                # timestamped_message = f"[{timestamp}] <{player}> {message}"
                if timestamped_message in chat_log:
                    continue
                # Adds raw line to chat log
                print(f"New message: {timestamped_message}")
                chat_log.add(timestamped_message)
                # If enabled, sends message as text
                if chat_notifications:
                    gmail_client.send_text(f"<{player}> {message}")

            print_title("PLAYER STATUSES", Colors.MAGENTA)

            # Gets player statuses from logs
            statuses = log_parser.get_statuses(logs)
            print(f"Recent statuses: {statuses}")
            # Updates player registry with statuses
            new_player_activity = log_parser.get_player_status_updates(
                statuses, online_players
            )
            print(f"\nNew activity: {new_player_activity}")
            # Send text about each player in joined set
            for player in new_player_activity[log_parser.JOINED_MESSAGE]:
                gmail_client.send_text(f"{player} just joined Trunkraft")
            # Send text about each player in left set
            for player in new_player_activity[log_parser.LEFT_MESSAGE]:
                gmail_client.send_text(f"{player} just left Trunkraft")

            print("\n" + "=" * TEXT_WIDTH)

            # End-of-loop actions
            loop_number += 1
            time.sleep(4)

    except KeyboardInterrupt:
        print("\nEnding communication.\n")


if __name__ == "__main__":
    main()
