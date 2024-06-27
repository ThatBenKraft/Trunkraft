import time
from collections import deque
from pathlib import Path

from registry import Registry
from smtp import send_text

# Constants for log paths
DEFAULT_WINDOWS_LOG_PATH = Path(
    "G:\\My Drive\\Minecraft\\Personal\\logs\\latest.log"
).as_posix()
DEFAULT_LINUX_LOG_PATH = Path("/home/ubuntu/minecraft/logs/latest.log").as_posix()
# Constant for how many lines from end of log to read
DEFAULT_LOG_LENGTH = 100

# Defines join/leave message flags
JOINED_MESSAGE = "joined the game"
LEFT_MESSAGE = "left the game"
STATUS_MESSAGES = {JOINED_MESSAGE: 1, LEFT_MESSAGE: -1}

# List of players to not notify about
IGNORED_PLAYERS = ["Optica"]


def main() -> None:
    """
    Runs main script actions.
    """
    sleep_time = float(input("Enter number of seconds between log checks: "))
    path_option = input("Enter w for windows and l for linux (l/y): ")

    if path_option.upper() == "W":
        log_path = DEFAULT_WINDOWS_LOG_PATH
    elif path_option.upper() == "L":
        log_path = DEFAULT_LINUX_LOG_PATH
    else:
        raise ValueError("Invalid option. Use 'w' for Windows or 'l' for Linux.")

    check_id = 1
    while True:
        check_logs(log_path, check_id)
        time.sleep(sleep_time)
        check_id += 1


def check_logs(
    log_path: str, check_id: int = 0, log_length: int = DEFAULT_LOG_LENGTH
) -> None:
    """
    Acquires lines from `latest.log` and analyzes contents.
    """
    print(f"\n[{check_id}] Checking logs...")
    try:
        with open(log_path, "r") as log_file:
            # Creates deque of log file containing only last lines
            last_lines = deque(log_file, maxlen=log_length)
    except FileNotFoundError:
        print(f"Log file not found at {log_path}")
        return

    # Player name associated with status
    last_statuses: dict[str, int] = {}
    # For each line in log in reverse order
    for line in reversed(last_lines):
        # Process the line for player status updates
        process_line(line, last_statuses)
    # Runs logic based on recent statuses
    parse_status(last_statuses)


def process_line(line: str, last_statuses: dict[str, int]) -> None:
    """
    Updates statuses based on current log line.
    """
    # Returns early if part of insecure chat message or player already found
    if "[Not Secure]" in line or any(player in line for player in last_statuses):
        return
    # For each message and associated status
    for message, status in STATUS_MESSAGES.items():
        # If the message is in the line:
        if message in line:
            # Acquires player name from line
            player = extract_player_name(line)
            # Log player status and print
            last_statuses[player] = status
            print(f">> {player} {message}")


def extract_player_name(line: str) -> str:
    """
    Extracts name string from log string.
    """
    # Creates target next to name
    TARGET = "[Server thread/INFO]: "
    # Finds starting position of substring
    start_position = line.find(TARGET)
    # Throw error if not found
    if start_position == -1:
        raise ValueError(f"'{TARGET}' not in line.")
    # Finds endpoints of name
    name_start = start_position + len(TARGET)
    name_end = line.find(" ", name_start)
    # Throw error if end is not found
    if name_end == -1:
        raise ValueError("Name does not have trailing space.")
    # Returns name
    return line[name_start:name_end]


def parse_status(last_statuses: dict[str, int]) -> None:
    """
    Runs update logic based on statuses and current list.
    """
    # Creates registry or loads existing
    registry = Registry()

    # For every played online:
    for player in registry:
        # If the player isn't in statuses:
        if player not in last_statuses:
            # Remove player from log
            registry.remove(player)

    # For player in statuses:
    for player, last_status in last_statuses.items():
        # If player left:
        if last_status == STATUS_MESSAGES[LEFT_MESSAGE]:
            # Remove player from log
            registry.remove(player)
        # If player joined:
        elif last_status == STATUS_MESSAGES[JOINED_MESSAGE]:
            # If player not in registry
            if player not in registry and player not in IGNORED_PLAYERS:
                # Sends text and waits
                print(f"Sending notification about {player}...")
                send_text(f"{player} joined Trunkraft")
                time.sleep(10)
            # Adds player to registry
            registry.add(player)

    # Prints current server members
    print(f"Currently in server: {registry}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nEnded logging.")
