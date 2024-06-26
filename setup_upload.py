from pathlib import Path

from server_ssh import SCP

# Creates paths
BASE_PATH = Path(__file__).parent
SETUP_PATH = BASE_PATH / "Server Setup"
TEXT_SCRIPT_PATH = BASE_PATH / "Player Text"
EC2_PATH = "/home/ubuntu/"


if __name__ == "__main__":
    # Creates SCP client
    scp_client = SCP()
    # Uploads setup files to EC2 path
    scp_client.upload(
        SETUP_PATH,
        EC2_PATH + "minecraft/",
        empty_contents=True,
        ignored_items=["libraries", "fabric-server-launch.jar", "mods"],
    )
    scp_client.upload(TEXT_SCRIPT_PATH, EC2_PATH)
    # Closes SCP connection
    scp_client.close()
