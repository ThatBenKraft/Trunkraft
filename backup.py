from datetime import date
from pathlib import Path

from server_ssh import SCP

# Establishes base paths
BASE_PATH = Path(__file__).parent
SETUP_PATH = BASE_PATH / "Server Setup"
EC2_PATH = "/home/ubuntu/minecraft/"

SETUP_FILENAMES = ("whitelist.json", "ops.json")

if __name__ == "__main__":
    # Creates local filepath based on date
    date = date.today()
    backup_path = BASE_PATH / "Backups" / f"{date.month}_{date.day}"

    # Creates SCP client
    scp_client = SCP()
    # Downloads from EC2 path
    scp_client.download(EC2_PATH + "trunkraft", backup_path)
    # Asks for confirmation before downloading config files
    config_confirm = input("\nWould you like to backup server config files? (y/n): ")
    # If yes:
    if config_confirm.upper() in "YES":
        # For each of the defined filenames:
        for filename in SETUP_FILENAMES:
            # Back up to setup folder
            scp_client.download(EC2_PATH + filename, SETUP_PATH)
    # Closes SCP connection
    scp_client.close()
