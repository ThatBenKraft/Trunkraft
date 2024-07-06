import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

import log_parser
from colors import Colors
from gmail import GmailClient
from log_parser import JOINED_MESSAGE, LEFT_MESSAGE
from registry import Registry

BASE_PATH = Path(__file__).parent
DATABASES_PATH = BASE_PATH / "databases/"
CHAT_LOG_PATH = DATABASES_PATH / "chat_log.json"
ONLINE_PLAYERS_REGISTRY_PATH = DATABASES_PATH / "online_players.json"
PENDING_MESSAGES_REGISTRY_PATH = DATABASES_PATH / "pending_messages.json"

# List of players to not notify about
IGNORED_PLAYERS = []

TEXT_WIDTH = 50


def print_title(line: str, color: str = Colors.RED) -> None:
    """
    Prints small title block for sections.
    """
    print(f"\n{color}" + f"[[    {line}    ]]".center(TEXT_WIDTH) + f"{Colors.RESET}\n")


def acquire_preference(name: str) -> bool:
    """
    Gets notification preference from terminal.
    """
    confirmation = input(
        f"\nWould you like to recieve {name} notifications? (y/n): "
    ).upper()
    return confirmation != "" and confirmation in "YES"


def main():
    """
    Runs main communication looping actions.
    """
    # Creates list of preferences
    preferences = [
        acquire_preference(name) for name in ("player joined", "player left", "chat")
    ]
    # Creates communications object
    communications = ServerCommunications(preferences)

    loop_number = 0

    try:
        while True:
            # Runs 2-way communications
            communications.run(loop_number)
            # End-of-loop actions
            loop_number += 1
            time.sleep(4)
    except KeyboardInterrupt:
        print("\nEnding communication.\n")


def compile_message(player: str, message: str, timestamp: str = "") -> str:
    """
    Builds minecraft console string from components. Adds current timestamp if not
    specified.
    """
    # If timestamp not specified:
    if not timestamp:
        # Gets UTC time
        utc_now = datetime.now(timezone.utc)
        # Creates timestamp to match log format
        timestamp = utc_now.strftime("%H:%M:%S")
    # Builds message
    return f"[{timestamp}] <{player}> {message}"


class ServerCommunications:

    def __init__(self, preferences: list[bool]) -> None:

        # Acquires log and function path from user
        self.log_path, self.message_function_path = log_parser.select_os_paths()
        # Creates Gmail client
        self.gmail_client = GmailClient()
        # Creates registries for online players, chat log, and pending messages
        self.online_players = Registry(ONLINE_PLAYERS_REGISTRY_PATH)
        self.chat_log = Registry(CHAT_LOG_PATH, max_length=100)
        self.pending_messages = Registry(PENDING_MESSAGES_REGISTRY_PATH, data_type=dict)
        # Gets notification preferences from console
        self.PLAYER_JOINED_NOTIFICATIONS = preferences[0]
        self.PLAYER_LEFT_NOTIFICATIONS = preferences[1]
        self.CHAT_NOTIFICATIONS = preferences[2]

    def run(self, loop_number: int):
        """
        Runs 2-way server communications.
        """

        print_title(str(loop_number), Colors.GREEN)
        print_title("MESSAGES FROM PHONE TO SERVER")
        # Processes messages from phone to server
        self.process_text_messages()

        print_title("MESSAGES FROM SERVER TO PHONE")
        # Acquires logs from file
        logs = log_parser.get_logs(self.log_path)
        # Processes messages from server to phone
        print_title("CHAT MESSAGES", Colors.MAGENTA)
        self.process_chat_messages(logs)
        print_title("PLAYER STATUSES", Colors.MAGENTA)
        self.process_statuses(logs)

        print("\n" + "=" * TEXT_WIDTH)

    def process_text_messages(self) -> None:
        """
        Processes messages from phone to server.
        """
        # Gets unread emails
        unread_emails = self.gmail_client.get_email(unread=True)
        print(f"Unread emails: ", end="")
        # For each unread email:
        for email in unread_emails:
            # Gets message from attachment
            message = self.gmail_client.read_text_attachment(email)
            print(f"[ {message} ]", end=" ")
            # Adds details to message
            compiled_message = compile_message("Server", message)
            # Adds compiled message as key to raw message to pending dict
            if compiled_message not in self.pending_messages:
                self.pending_messages[compiled_message] = message
        print("")

        # With function file:
        with open(self.message_function_path, "w") as function_file:
            # For email in list:
            print(f"Messages written to function file: ", end="")
            function_file.write(f"## Incoming server messages:\n\n")
            # For the compiled and raw version of each pending message:
            for compiled_message, message in self.pending_messages.items():
                # Removes message if already in chat log
                if compiled_message in self.chat_log:
                    self.pending_messages.remove(compiled_message)
                else:
                    # Writes message as command in function file
                    command = f"say {message}\n"
                    print(f"[ {command} ]", end=" ")
                    function_file.write(command)
        print("")

    def process_chat_messages(self, logs: deque) -> None:
        """
        Sends notifications about most recent chat messages.
        """
        # Gets chat messages from logs
        chat_messages = log_parser.get_messages(logs)
        # Iterating over details of each chat message:
        for player, message, timestamp in chat_messages:
            # Continue to next message if in chat log
            timestamped_message = compile_message(player, message, timestamp)
            # Skips if chat already in log
            if timestamped_message in self.chat_log:
                continue
            # Adds line to chat log
            print(f"New message: {timestamped_message}")
            self.chat_log.add(timestamped_message)
            # If enabled, sends message as text
            if self.CHAT_NOTIFICATIONS:
                self.gmail_client.send_text(f"<{player}> {message}")

    def process_statuses(self, logs: deque[str]) -> None:
        """
        Sends notifications about most recent player statuses.
        """
        # Gets player statuses from logs
        player_statuses = log_parser.get_statuses(logs)
        print(f"Recent statuses: {player_statuses}")

        # Iterating over player statuses:
        for player, last_status in player_statuses.items():
            # If player last joined and not in registry:
            if last_status == JOINED_MESSAGE and player not in self.online_players:
                # Add to registry
                self.online_players.add(player)
                # Send text if preference set
                if self.PLAYER_JOINED_NOTIFICATIONS and player not in IGNORED_PLAYERS:
                    self.gmail_client.send_text(f"{player} just joined Trunkraft")
            # If player last left and in registry:
            elif last_status == LEFT_MESSAGE and player in self.online_players:
                # Remove from registry
                self.online_players.remove(player)
                # Send text if preference set
                if self.PLAYER_LEFT_NOTIFICATIONS and player not in IGNORED_PLAYERS:
                    self.gmail_client.send_text(f"{player} just left Trunkraft")


if __name__ == "__main__":
    main()
