"""
Used for entering ssh with the aws client.
"""

from pathlib import Path

import paramiko
from scp import SCPClient

EC2_SERVER_PATH = Path(Path(__file__).parent / "ec2_server.txt")

# Acquires server public IPv4 DNS from text file
with open(EC2_SERVER_PATH, "r") as file:
    # Reads the first line
    DEFAULT_SERVER = file.readline()
# Defines login credentials
DEFAULT_PORT = 22
DEFAULT_USER = "ubuntu"


# Constants for various paths
# Local
LOCAL_BASE_PATH = Path(__file__).parents[1]
DEFAULT_KEY_PATH = LOCAL_BASE_PATH / "ubuntu_login.pem"
LOCAL_DATAPACK_PATH = LOCAL_BASE_PATH / "Trunkraft Datapack"
# EC2
EC2_PATH = "/home/ubuntu/"
EC2_DATAPACK_PATH = EC2_PATH + "minecraft/trunkraft/datapacks/"


class SCP:
    """
    Class for SCP file transfers.
    """

    def __init__(
        self,
        server: str = DEFAULT_SERVER,
        port: int = DEFAULT_PORT,
        user: str = DEFAULT_USER,
        key_path: Path | str = DEFAULT_KEY_PATH,
    ) -> None:
        """
        Initializes the SCP class and establishes an SSH connection.
        """
        try:
            # Creates key from file
            key = paramiko.RSAKey.from_private_key_file(str(key_path))
            # Creates SSH client
            ssh_client = paramiko.SSHClient()
            # Some stackoverflow bs to make it work
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # Connects to client
            print("\nConnecting to EC2...")
            ssh_client.connect(server, port, user, pkey=key)
            print("Connected.")
            # Creates SCP client from SSH transport
            self.client = SCPClient(ssh_client.get_transport())  # type: ignore
        except Exception as error:
            # Prints errors
            print(f"Error connecting to server: {error}")

    def upload(
        self,
        local_path: Path | str,
        remote_path: str,
        empty_contents: bool = False,
        ignored_items: list[str] = [],
    ) -> None:
        """
        Uploads item/s to the EC2 server.
        """
        try:
            print("\nUploading:")
            # Asserts path type
            local_path = Path(local_path)
            # If directory contents are to be emptied:
            if local_path.is_dir() and empty_contents:
                # For each item in directory:
                for item_path in local_path.iterdir():
                    # Skips if item is to be ignored
                    if item_path.name in ignored_items:
                        continue
                    # List and upload item
                    print(f"[ {item_path.name} ]")
                    self.client.put(item_path, remote_path, recursive=True)
            else:
                # List and upload item
                print(f"[ {local_path.name} ]")
                self.client.put(local_path, remote_path, recursive=True)
            print("Finished transfer.")
        except Exception as error:
            # Prints errors
            print(f"Error during upload: {error}")

    def download(self, remote_path: str, local_path: Path | str) -> None:
        """
        Downloads item/s from EC2 server.
        """
        try:
            print(f"Backing up: {remote_path}. . .")
            # Downloads item from server
            self.client.get(remote_path, local_path, recursive=True)  # type: ignore
            print("Finished transfer.")
        except Exception as error:
            # Prints errors
            print(f"Error during download: {error}")

    def close(self) -> None:
        """
        Closes SCP channel.
        """
        print("\nClosing SCP channel.\n")
        self.client.close()

    def __exit__(self) -> None:
        """
        Defines shutdown behavior.
        """
        self.close()
