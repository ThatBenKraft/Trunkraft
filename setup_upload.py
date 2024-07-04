from pathlib import Path

from communication.server_ssh import (
    EC2_DATAPACK_PATH,
    EC2_PATH,
    LOCAL_DATAPACK_PATH,
    SCP,
)

# Creates paths
BASE_PATH = Path(__file__).parent
SETUP_PATH = BASE_PATH / "Server Setup"
COMMUNICATIONS_PATH = BASE_PATH / "communication"


if __name__ == "__main__":
    # Creates SCP client
    scp_client = SCP()
    # Uploads setup files to EC2 path
    # scp_client.upload(
    #     SETUP_PATH,
    #     EC2_PATH + "minecraft/",
    #     empty_contents=True,
    #     ignored_items=["libraries", "fabric-server-launch.jar"],
    # )
    scp_client.upload(
        COMMUNICATIONS_PATH,
        EC2_PATH + "communication/",
        empty_contents=True,
        ignored_items=["databases", "Log Logic.xlsx", "__pycache__"],
    )
    scp_client.upload(LOCAL_DATAPACK_PATH, EC2_DATAPACK_PATH)
    # Closes SCP connection
    scp_client.close()
