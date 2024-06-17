from datetime import date
from pathlib import Path

import server_ssh

# Establishes base paths
BASE_PATH = Path(__file__).parent
EC2_PATH = "/home/ubuntu/minecraft/trunkraft"


if __name__ == "__main__":
    # Creates local filepath based on date
    date = date.today()
    backup_path = BASE_PATH / "Backups" / f"{date.month}_{date.day}b"
    # Downloads from EC2 path
    server_ssh.download(EC2_PATH, backup_path)
