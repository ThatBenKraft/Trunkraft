"""
Used for sending admin a text when a player joins the server.
"""

import time
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path

from registry import Registry
from server_ssh import EC2_DATAPACK_PATH, LOCAL_DATAPACK_PATH

# Constants for log paths
DEFAULT_WINDOWS_LOG_PATH = Path(
    "G:\\My Drive\\Minecraft\\Personal\\logs\\latest.log"
).as_posix()
DEFAULT_LINUX_LOG_PATH = Path("/home/ubuntu/minecraft/logs/latest.log").as_posix()
# Constants for mcfunction file paths
LOCAL_MESSAGE_FUNCTION_PATH = (
    LOCAL_DATAPACK_PATH / "data/trunkraft/function/texting/new_messages.mcfunction"
)
EC2_MESSAGE_FUNCTION_PATH = (
    EC2_DATAPACK_PATH
    + "Trunkraft Datapack/data/trunkraft/function/texting/new_messages.mcfunction"
)
# Various constants
DEFAULT_LOG_LENGTH = 100
DEFAULT_SLEEP_TIME = 60 * 5

# Defines join/leave message flags
# JOINED_MESSAGE = "joined the game"
# LEFT_MESSAGE = "left the game"
# STATUS_MESSAGES = {JOINED_MESSAGE: 1, LEFT_MESSAGE: -1}
JOINED_MESSAGE = "joined the game"
LEFT_MESSAGE = "left the game"

SERVER_INFO_TARGET = "[Server thread/INFO]: "
NOT_SECURE_TARGET = "[Not Secure] "

PAIRED_BRACES = {"<": ">", "[": "]"}


def main() -> None:
    """
    Upkeeps player registry
    """
    sleep_time = float(input("Enter number of seconds between log checks: "))

    if not sleep_time:
        sleep_time = DEFAULT_SLEEP_TIME

    log_path, _ = select_os_paths()

    # Creates registry or loads existing
    online_players = Registry()

    try:
        check_id = 1
        while True:
            # Gets logs
            logs = get_logs(log_path, check_id)
            # Runs registry actions based on last player statuses
            last_statuses = get_statuses(logs)
            # Updates registry and notifies about player joins
            get_player_status_updates(last_statuses, online_players)
            # Waits before running again
            time.sleep(sleep_time)
            check_id += 1
    except KeyboardInterrupt:
        print("\nStopping log reading.\n")


def select_os_paths() -> tuple[str, str]:
    """
    Asks user for input on which system to use. Returns corresponding log and
    message function paths.
    """
    # Gets path choice
    path_choice = input("Enter w for windows and l for linux (w/l): ").upper()
    # Splits choice between windows and linux
    if path_choice == "W":
        return DEFAULT_WINDOWS_LOG_PATH, str(LOCAL_MESSAGE_FUNCTION_PATH)
    elif path_choice == "L":
        return DEFAULT_LINUX_LOG_PATH, str(EC2_MESSAGE_FUNCTION_PATH)
    else:
        raise ValueError("Invalid option. Use 'w' for Windows or 'l' for Linux.")


def get_logs(log_path: str, log_length: int = DEFAULT_LOG_LENGTH) -> deque[str]:
    """
    Acquires lines from `latest.log` and analyzes contents.
    """
    print(f"\nChecking logs...")
    try:
        with open(log_path, "r") as log_file:
            # Creates deque of log file containing only last lines
            logs = deque(log_file, log_length)
            # Strips newlines from ends of log lines
            return deque(log.strip() for log in logs)
    except FileNotFoundError:
        print(f"Log file not found at {log_path}")
    return deque()


def get_statuses(logs: deque[str]) -> dict[str, str]:
    """
    Acquires latest player status dictionary from logs. Returns dictionary of
    player and status.
    """
    # Player name associated with status
    last_statuses: dict[str, str] = {}
    # For each line in log in reverse order
    for line in reversed(logs):
        # Gets player and status from line
        player_status: tuple[str, str] = extract_player_status(line)  # type: ignore
        # If player status is found:
        if player_status:
            # Unpacks components
            player, status = player_status
            # If player not already in statuses
            if player not in last_statuses:
                # Adds player and status to dictionary
                last_statuses[player] = status
    # Returns with populated statuses
    return last_statuses


def extract_player_status(line: str) -> tuple[str, str] | None:
    """
    Gets player and corresponding status from line. Returns None if line is not
    status.
    """
    # Returns if neither server info target nor either status message are in line
    if SERVER_INFO_TARGET not in line or (
        JOINED_MESSAGE not in line and LEFT_MESSAGE not in line
    ):
        return
    # Strips line of server info
    stripped_line = skip_item(line, SERVER_INFO_TARGET)
    # Returns early if any braces appear in stripped line
    if any(brace in stripped_line for brace in PAIRED_BRACES):
        return
    # Finds end of name
    name_end = stripped_line.find(" ")
    # Raises error if invalid line
    if name_end == -1:
        raise ValueError("Name does not have trailing space.")
    # Gets name and status from stripped line
    name = stripped_line[:name_end]
    status = stripped_line[name_end + 1 :]
    # Returns name and status
    return name, status


def get_messages(logs: deque[str]) -> list[tuple[str, str, str]]:
    """
    Acquires chat messages from logs. Returns list of player, message, and
    timestamp.
    """
    messages: list[tuple[str, str, str]] = []
    # For each line in logs:
    for line in logs:
        # Gets components from log line
        message_components: tuple[str, str, str] = extract_player_message(line)  # type: ignore
        # If message components are found:
        if message_components:
            # Add components to list
            messages.append(message_components)
    # Returns list of messages
    return messages


def extract_player_message(line: str) -> tuple[str, str, str] | None:
    """
    Gets player and corresponding message from line. Returns None if line is not
    message.
    """
    # Returns if not server info
    if SERVER_INFO_TARGET not in line:
        return
    # Strips line of server info
    stripped_line = skip_item(line, SERVER_INFO_TARGET)
    # Strips line of Not Secure component if present
    if NOT_SECURE_TARGET in stripped_line:
        stripped_line = skip_item(stripped_line, NOT_SECURE_TARGET)
    # Gets brace type
    brace_type = stripped_line[0]
    # Returns if brace is not present at start of line
    if brace_type not in PAIRED_BRACES:
        return
    closing_brace = PAIRED_BRACES[brace_type]
    # Finds next space
    next_space = stripped_line.find(" ")
    if next_space == -1:
        raise ValueError(f"Invalid line: {line}")
    # If next space is not next to closing brace of name:
    if stripped_line[next_space - 1] != closing_brace:
        return
    # Finds end of name
    name_end = stripped_line.find(closing_brace)
    # Raises error if invalid line
    if name_end == -1:
        raise ValueError("Name does not have trailing brace.")
    # Gets name and message from stripped line
    name = stripped_line[1:name_end]
    message = stripped_line[name_end + 2 :]
    # Gets timestamp from beginning of message
    timestamp = line[1 : line.find("]")]
    # Returns name and message
    return name, message, timestamp


def skip_item(line: str, item: str) -> str:
    """
    Skips all content to the left of and including item in line.
    """
    # Finds position of item
    position = line.find(item)
    # Raise error if item is not found
    if position == -1:
        raise ValueError(f"Item {item} not in line {line}")
    # Returns stripped line
    return line[position + len(item) :]


def get_player_status_updates(
    last_statuses: dict[str, str], online_players: Registry
) -> dict[str, set[str]]:
    """
    Updates registry based on last player statuses and notifies on player joins.
    Returns dictionary with status messages keys to players who have just
    become corresponding status.
    """
    # For every player online:
    for player in online_players:
        # If the player isn't in statuses:
        if player not in last_statuses:
            # Remove player from log
            online_players.remove(player)

    # Creates list for newly joined players
    new_player_activity: dict[str, set[str]] = defaultdict(set)

    # For player in statuses:
    for player, last_status in last_statuses.items():
        # If player left and is in registry:
        if last_status == LEFT_MESSAGE and player in online_players:
            # Adds player to newly left set
            new_player_activity[LEFT_MESSAGE].add(player)
            # Remove player from log
            online_players.remove(player)
        # If player joined and not in registry:
        elif last_status == JOINED_MESSAGE and player not in online_players:
            # Adds player to newly joined set
            new_player_activity[JOINED_MESSAGE].add(player)
            # Adds player to registry
            online_players.add(player)

    # Prints current server members
    print(f"Currently in server: {online_players}")
    return new_player_activity


if __name__ == "__main__":
    main()
