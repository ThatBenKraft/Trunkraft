from pathlib import Path

import openpyxl

from communication.server_ssh import SCP
from setup_upload import EC2_DATAPACK_PATH, LOCAL_DATAPACK_PATH

# Defines base player height
BASE_HEIGHT_M = 1.8

# Specifies data columns
NAME_COL = 1
USERNAME_COL = 2
HEIGHT_IN_COL = 3


# Creates paths
WORKBOOK_PATH = Path(__file__).parent / "Player Heights.xlsx"
FUNCTION_PATH = LOCAL_DATAPACK_PATH / "data/trunkraft/function/player_size.mcfunction"


def update_heights() -> None:
    """
    Updates mcfunction with correct player heights based on Excel data.
    """
    try:
        # Opening mcfunction file:
        with open(FUNCTION_PATH, "w") as file:
            # Opens excel file and creates sheet
            workbook = openpyxl.load_workbook(WORKBOOK_PATH, data_only=True)
            sheet = workbook.active
            # Counting down the rows:
            for row in range(2, 100):
                # Defines function for data acquisition
                sheet_data = lambda column: sheet.cell(row, column).value  # type: ignore
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
    # Catches errors
    except Exception as error:
        print(f"Error updating heights: {error}")


if __name__ == "__main__":
    # Updates function file from spreadsheet
    update_heights()
    # Creates SCP client
    scp_client = SCP()
    # Uploads datapack to server
    scp_client.upload(LOCAL_DATAPACK_PATH, EC2_DATAPACK_PATH)
    # Closes SCP connection
    scp_client.close()
