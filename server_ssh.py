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
DEFAULT_KEY_PATH = Path("C:/Users/Ben/.ssh/ubuntu_login.pem")


def create_ssh_client(
    server=DEFAULT_SERVER,
    port=DEFAULT_PORT,
    user=DEFAULT_USER,
    key_path=DEFAULT_KEY_PATH,
) -> paramiko.SSHClient:
    """
    Creates ssh client from credentials.
    """
    key = paramiko.RSAKey.from_private_key_file(key_path)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("\nConnecting...")
    client.connect(server, port, user, pkey=key)
    print("Connected.\n")
    return client


def create_scp_client(
    server=DEFAULT_SERVER,
    port=DEFAULT_PORT,
    user=DEFAULT_USER,
    key_path=DEFAULT_KEY_PATH,
) -> SCPClient:
    """
    Creates scp client from credentials.
    """
    # Creates ssh client
    ssh = create_ssh_client(server, port, user, key_path)
    # Converts to scp client
    return SCPClient(ssh.get_transport())


def upload(local_path: Path, remote_path: str, empty_contents=False) -> None:
    """
    Uploads item/s to EC2 server.
    """
    try:
        # Creates SCP client
        scp = create_scp_client()
        print("Uploading:")
        # If directory contents are to be emptied:
        if local_path.is_dir() and empty_contents:
            # For each item in directory:
            for item_path in local_path.iterdir():
                # List and upload item
                print(f"[ {item_path.name} ]")
                scp.put(item_path, remote_path, recursive=True)
        else:
            # List and upload item
            print(f"[ {local_path.name} ]")
            scp.put(local_path, remote_path, recursive=True)
    except Exception as e:
        # Prints errors
        print("Error:", str(e))
    finally:
        # Closes SCP connection
        scp.close()
        print("Finished transfer.")


def download(remote_path: str, local_path: Path) -> None:
    """
    Downloads item/s from EC2 server.
    """
    try:
        # Creates SCP client
        scp = create_scp_client()
        print(f"Backing up: {remote_path}. . .")
        scp.get(remote_path, local_path, recursive=True)
    except Exception as e:
        # Prints errors
        print("Error:", str(e))
    finally:
        # Closes SSH connection
        scp.close()
        print("Finished transfer.")
