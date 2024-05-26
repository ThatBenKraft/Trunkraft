def extract_drive_id(link: str) -> str | None:
    """
    Acquires ID string from link.
    """
    try:
        # Gets id string, splitting at /d/ and next backslash
        drive_id = link.split("/d/")[1].split("/")[0]
        return drive_id
    except IndexError:
        return None

def convert_link() -> None:
    """
    Runs main link maker actions.
    """
    # Requests link and new filename
    raw_link = input("\nPlease enter raw Google Drive link: ")
    filename = input("Please enter a filename: ")
    # Acquires IF from link
    drive_id = extract_drive_id(raw_link)
    # Prints link info if available
    if drive_id:
        print(f"\nLINUX COMMAND:\n\nwget --no-check-certificate 'https://drive.google.com/uc?id={drive_id}' -O '{filename}'")
    else:
        print("Unable to extract Google Drive ID from the link.")
    print("")

if __name__ == "__main__":
    convert_link()