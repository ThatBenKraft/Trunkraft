from pathlib import Path

import openpyxl

import server_ssh

BASE_MC_HEIGHT = 1.8

NAME_COL = 1
USERNAME_COL = 2
HEIGHT_COL = 4

workbook_path = "G:/My Drive/Trunkraft/Player Heights.xlsx"
datapack_path = Path(__file__).parent / "Trunkraft_Datapack"
function_path = datapack_path / "data/trunkraft/functions/player_size.mcfunction"
ec2_path = "/home/ubuntu/minecraft/trunkraft/datapacks/"


def update_heights() -> None:

    with open(function_path, "w") as file:

        workbook = openpyxl.load_workbook(workbook_path, data_only=True)
        sheet = workbook.active

        for row in range(2, 100):

            sheet_data = lambda column: sheet.cell(row=row, column=column).value
            # Acquires usernames and names
            name = sheet_data(NAME_COL)
            username = sheet_data(USERNAME_COL)

            if name is None:
                break
            if username is None:
                continue

            height = sheet_data(HEIGHT_COL)
            adjusted_height = height / BASE_MC_HEIGHT

            file.write(
                f"attribute {username} minecraft:generic.scale base set {adjusted_height:.3f}\n"
            )


def upload_datapack() -> None:

    try:
        scp = server_ssh.create_scp_client()
        scp.put(datapack_path, ec2_path, recursive=True)
    except Exception as e:
        print("Error:", str(e))
    finally:
        # Close SSH connection
        scp.close()

    print("Finished transfer.")


if __name__ == "__main__":
    update_heights()

    upload_datapack()
