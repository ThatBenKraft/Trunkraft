"""
Used for entering ssh with the aws client.
"""

from pathlib import Path

import paramiko
from scp import SCPClient

# Acquires server public IPv4 DNS from text file
with open("ec2_server.txt", "r") as file:
    # Reads the first line
    DEFAULT_SERVER = file.readline()
# Defines login credentials
DEFAULT_PORT = 22
DEFAULT_USER = "ubuntu"
# Finds key from file
BASE_PATH = Path(__file__).parent
DEFAULT_KEY_PATH = BASE_PATH / "ubuntu_login.pem"


class SCP:
    """
    Class for SCP file transfers.
    """

    def __init__(
        self,
        server: str = DEFAULT_SERVER,
        port: int = DEFAULT_PORT,
        user: str = DEFAULT_USER,
        key_path: Path = DEFAULT_KEY_PATH,
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
            print("Connected.\n")
            # Creates SCP client from SSH transport
            self.client = SCPClient(ssh_client.get_transport())  # type: ignore
        except Exception as error:
            # Prints errors
            print(f"Error connecting to server: {error}")
            raise

    def upload(
        self,
        local_path: Path,
        remote_path: str,
        empty_contents: bool = False,
        ignored_items: list[str] = [],
    ) -> None:
        """
        Uploads item/s to the EC2 server.
        """
        try:
            print("Uploading:")
            # If directory contents are to be emptied:
            if local_path.is_dir() and empty_contents:
                # For each item in directory:
                for item_path in local_path.iterdir():
                    # List and upload item
                    if item_path.name not in ignored_items:
                        print(f"[ {item_path.name} ]")
                        self.client.put(item_path, remote_path, recursive=True)
            else:
                # List and upload item
                print(f"[ {local_path.name} ]")
                self.client.put(local_path, remote_path, recursive=True)
        except Exception as error:
            # Prints errors
            print(f"Error during upload: {error}")
        finally:
            # Closes SCP connection
            print("Finished transfer.")

    def download(self, remote_path: str, local_path: Path) -> None:
        """
        Downloads item/s from EC2 server.
        """
        try:
            print(f"Backing up: {remote_path}. . .")
            # Downloads item from server
            self.client.get(remote_path, local_path, recursive=True)  # type: ignore
        except Exception as error:
            # Prints errors
            print(f"Error during download: {error}")
        finally:
            # Closes SSH connection
            print("Finished transfer.")

    def close(self) -> None:
        """
        Closes SCP channel.
        """
        print("\nClosing SCP channel.\n")
        self.client.close()

    def __exit__(self):
        """
        Defines shutdown behavior.
        """
        self.close()
