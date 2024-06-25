import time
from collections import deque
from pathlib import Path

from registry import Registry
from smtp import send_text

# Defines paths
LOG_PATH = Path("G:\\My Drive\\Minecraft\\Personal\\logs\\latest.log").as_posix()
# Defines join/leave message flags
STATUS_MESSAGES = ("joined the game", "left the game")

JOINED = 1
LEFT = -1


def main() -> None:
    """
    Runs main script actions.
    """
    # Opens log file
    with open(LOG_PATH, "r") as log_file:
        # Creates queue of last 100 lines
        last_lines = deque(log_file, 100)
    # Player name associated with status:
    # 1  = most recently joined
    # -1 = most recently left
    logged_statuses: dict[str, int] = {}
    # For each line in log in reverse order
    for line in reversed(last_lines):
        # print(line.strip()[:100])
        # Process the line for player status updates
        process_line(line, logged_statuses)
    # Runs logic based on recent statuses
    parse_status(logged_statuses)


def process_line(line: str, logged_statuses: dict[str, int]) -> None:
    """
    Updates statuses based on current log line.
    """
    # If join or leave message in line:
    if any(message in line for message in STATUS_MESSAGES):
        # Returns early if part of insecure chat message
        if "[Not Secure]" in line:
            return
        # Acquires player name from line
        player = extract_player_name(line)

        # For each message and corresponding status:
        for message, status in zip(STATUS_MESSAGES, (JOINED, LEFT)):
            # If the message appears in the line and player has not been seen yet:
            if message in line and player not in logged_statuses:
                # Log player status and print
                logged_statuses[player] = status
                print(f"{player} {message}")


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


def parse_status(logged_statuses: dict[str, int]) -> None:
    """
    Runs update logic based on statuses and current list.
    """
    registry = Registry()
    # For every played online:
    for player in registry:
        # If the player isn't in statuses:
        if player not in logged_statuses:
            # Remove player from log
            registry.remove(player)

    # For player in statuses:
    for player in logged_statuses:
        # Get status of player
        logged_status = logged_statuses[player]
        # If player left:
        if logged_status == LEFT:
            # Remove player from log
            registry.remove(player)
        # If player joined:
        if logged_status == JOINED:
            # If player not in registry
            if player not in registry:
                # Sends text and waits
                print(f"Sending notification about {player}...")
                send_text(player)
                time.sleep(10)
            # Adds player to registry
            registry.add(player)

    # Prints current server members
    print(f"Currently in server: {registry}")


if __name__ == "__main__":
    main()
