from pathlib import Path

import openpyxl

import server_ssh

# Defines base player height
BASE_HEIGHT_M = 1.8

# Specifies data columns
NAME_COL = 1
USERNAME_COL = 2
HEIGHT_IN_COL = 3

base_path = Path(__file__).parent

# Creates paths
WORKBOOK_PATH = base_path / "Player Heights.xlsx"
LOCAL_DATAPACK_PATH = base_path / "Trunkraft Datapack"
LOCAL_FUNCTION_PATH = (
    LOCAL_DATAPACK_PATH / "data/trunkraft/function/player_size.mcfunction"
)
EC2_DATAPACK_PATH = "/home/ubuntu/minecraft/trunkraft/datapacks/"


def update_heights() -> None:
    """
    Updates mcfunction with correct player heights.
    """
    # Opening mcfunction file:
    with open(LOCAL_FUNCTION_PATH, "w") as file:
        # Opens excel file and creates sheet
        workbook = openpyxl.load_workbook(WORKBOOK_PATH, data_only=True)
        sheet = workbook.active
        # Counting down the rows:
        for row in range(2, 100):
            # Defines function for data acquisition
            sheet_data = lambda column: sheet.cell(row=row, column=column).value  # type: ignore
            # Acquires usernames and names
            name = sheet_data(NAME_COL)
            username = sheet_data(USERNAME_COL)
            # If there is no mroe names, stop
            if name is None:
                break
            # If there is no username, skip
            if username is None:
                continue
            # Acquires heights
            height_in = int(sheet_data(HEIGHT_IN_COL))  # type: ignore
            height_m = height_in / 39.37
            # Scales height to player
            adjusted_scale = height_m / BASE_HEIGHT_M
            # Writes attribut and scoreboard commands in function
            file.write(
                f"attribute {username} minecraft:generic.scale base set {adjusted_scale:.3f}\n"
                f"scoreboard players set {username} height_in {height_in}\n\n"
            )
        # Writes scheduling command for function
        file.write("schedule function trunkraft:player_size 3s\n")


if __name__ == "__main__":
    # Runs main script actions
    update_heights()

    server_ssh.upload(LOCAL_DATAPACK_PATH, EC2_DATAPACK_PATH)
