SERVER_INFO_TARGET = "[Server thread/INFO]: "
NOT_SECURE_TARGET = "[Not Secure] "

PAIRED_BRACES = {"<": ">", "[": "]"}

STATUS_MESSAGE_TARGETS = ("joined the game", "left the game")


def skip_item(line: str, item: str) -> str:
    position = line.find(item)
    if position == -1:
        raise ValueError(f"Item {item} not in line {line}")
    return line[position + len(item) :]


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


def extract_player_status(line: str) -> tuple[str, str] | None:
    # Return early if neither server info target nor either status message
    # present in line, or braces are in line
    if SERVER_INFO_TARGET not in line or all(
        status not in line for status in STATUS_MESSAGE_TARGETS
    ):
        return

    stripped_line = skip_item(line, SERVER_INFO_TARGET)

    # Returns early if any braces appear in stripped line
    if any(brace in stripped_line for brace in PAIRED_BRACES):
        return

    name_end = stripped_line.find(" ")

    if name_end == -1:
        raise ValueError("Name does not have trailing space.")

    name = stripped_line[:name_end]
    message = stripped_line[name_end + 1 :]

    return name, message


test_lines = [
    "[03:13:45] [Server thread/INFO]: Loaded stuff",
    "[03:13:45] [Server thread/INFO]: <ben> stuff",
    "[03:13:45] [Server thread/INFO]: <server> bill joined the game",
    "[03:13:45] [Server thread/INFO]: [Not Secure] [Server] stuff",
    "[15:29:56] [User Authenticator #13/INFO]: UUID of player Optica is bd6171",
    "[15:25:37] [Server thread/INFO]: datapack disable trunkraft<--[HERE]",
    "[15:29:57] [Server thread/INFO]: Optica joined the game",
    "[18:58:24] [Server thread/INFO]: [Optica: Reloading!]",
    "[18:58:32] [Server thread/INFO]: [Optica: Running function trunkraft:texting/tellraw]",
]

for line in test_lines:
    print(line)
    pairing = extract_player_message(line)
    if pairing:
        print(pairing)
    else:
        print("Not status")
