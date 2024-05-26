from datetime import date
from pathlib import Path

import server_ssh

# Establishes base paths
ec2_path = "/home/ubuntu/minecraft/"
WORLD_NAME = "trunkraft"

# Creates list of files and directories to backup
BACKUP_FILES = (
    WORLD_NAME,
    f"{WORLD_NAME}_nether",
    f"{WORLD_NAME}_the_end",
    "server.properties",
    "whitelist.json",
)


if __name__ == "__main__":

    # Creates local filepath based on date
    date = date.today()
    backup_path = str(Path(__file__).parent / "Backups" / f"{date.month}_{date.day}")

    try:
        scp = server_ssh.create_scp_client()

        print(f"Backing up to: {backup_path}. . .\n")

        for file in BACKUP_FILES:

            current_path = ec2_path + file
            print(f"Backing up: {current_path}. . .")
            scp.get(current_path, backup_path, recursive=True)
    except Exception as e:
        print("Error:", str(e))
    finally:
        # Close SSH connection
        scp.close()

    print("Finished transfer.")
