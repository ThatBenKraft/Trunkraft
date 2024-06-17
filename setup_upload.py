from pathlib import Path

import server_ssh

# Creates paths
BASE_PATH = Path(__file__).parent
SETUP_PATH = BASE_PATH / "Server Setup"
EC2_PATH = "/home/ubuntu/scp_testing/"


if __name__ == "__main__":
    # Uploads setup files to EC2 path
    server_ssh.upload(SETUP_PATH, EC2_PATH, empty_contents=True)
