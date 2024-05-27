from pathlib import Path

import openpyxl

import server_ssh

# Defines base player height
BASE_HEIGHT_M = 1.8

# Specifies data columns
NAME_COL = 1
USERNAME_COL = 2
HEIGHT_IN_COL = 3
HEIGHT_M_COL = 4

# Creates paths
workbook_path = "G:/My Drive/Trunkraft/Player Heights.xlsx"
datapack_path = Path(__file__).parent / "Trunkraft_Datapack"
function_path = datapack_path / "data/trunkraft/functions/player_size.mcfunction"
ec2_path = "/home/ubuntu/minecraft/trunkraft/datapacks/"


def update_heights() -> None:
    """
    Updates mcfunction with correct player heights.
    """
    # Opening mcfunction file:
    with open(function_path, "w") as file:
        # Opens excel file and creates sheet
        workbook = openpyxl.load_workbook(workbook_path, data_only=True)
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
            height_m = float(sheet_data(HEIGHT_M_COL))  # type: ignore
            # Scales height to player
            adjusted_scale = height_m / BASE_HEIGHT_M
            # Writes attribut and scoreboard commands in function
            file.write(
                f"attribute {username} minecraft:generic.scale base set {adjusted_scale:.3f}\n"
                f"scoreboard players set {username} height_in {height_in}\n\n"
            )
        # Writes scheduling command for function
        file.write("schedule function trunkraft:player_size 5s")


def upload_datapack() -> None:
    """
    Uploads datapack to EC2 server.
    """
    try:
        # Creates SCP connection
        scp = server_ssh.create_scp_client()
        # Transfers datapack
        scp.put(datapack_path, ec2_path, recursive=True)
    except Exception as e:
        # Prints errors
        print("Error:", str(e))
    finally:
        # Closes SCP connection
        scp.close()

    print("Finished transfer.")


if __name__ == "__main__":
    # Runs main script actions
    update_heights()

    upload_datapack()
