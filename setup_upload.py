from pathlib import Path

from server_ssh import SCP

# Creates paths
BASE_PATH = Path(__file__).parent
SETUP_PATH = BASE_PATH / "Server Setup"
EC2_PATH = "/home/ubuntu/scp_testing/"


if __name__ == "__main__":
    # Creates SCP client
    scp_client = SCP()
    # Uploads setup files to EC2 path
    scp_client.upload(SETUP_PATH, EC2_PATH, empty_contents=True)
    # Closes SCP connection
    scp_client.close()
