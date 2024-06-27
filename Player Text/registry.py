import json
from pathlib import Path
from typing import Any, Generator

BASE_PATH = Path(__file__).parent
JSON_PATH = BASE_PATH / "registry.json"


class Registry:
    """
    Active registry that saves to a JOSN file.
    """

    def __init__(self, path: Path = JSON_PATH) -> None:
        """
        Active registry that saves to a JOSN file.
        """
        self._path = path
        self._data = []
        # If file exists
        if self._path.exists():
            try:
                # Opens and returns data
                with open(self._path, "r") as file:
                    self._data: list[str] = json.load(file)
                    # Checks for invalid data type
                    if not isinstance(self._data, list):
                        raise ValueError("Invalid data format in JSON file")
            # Handles decoding and other errors
            except json.JSONDecodeError:
                print(f"Error: Failed to decode JSON from {self._path}")
                self._data = []
            except (ValueError, IOError) as error:
                print(f"Error: {error}")
                self._data = []
        else:
            self._save_to_json()

    def __contains__(self, player: str) -> bool:
        return player in self._data

    def __iter__(self) -> Generator[str, Any, None]:
        for player in self._data:
            yield player

    def __str__(self) -> str:
        if self._data:
            return ", ".join(self._data)
        else:
            return "None"

    def _save_to_json(self) -> None:
        """
        Saves data to JSON file.
        """
        try:
            # Opens and writes data to JSON file
            with open(self._path, "w") as file:
                json.dump(self._data, file, indent=4)
        # Handles file writing errors
        except IOError as error:
            print(f"Error: Failed to write to {self._path}: {error}")

    def add(self, player: str) -> None:
        """
        Adds player to JSON registry.
        """
        # If player not already in registry:
        if player not in self._data:
            # Adds player
            self._data.append(player)
            # Saves registry to JSON
            self._save_to_json()

    def remove(self, player: str) -> None:
        """
        Removes player from JSON registry.
        """
        # If player is in registry:
        if player in self._data:
            # Removes player
            self._data.remove(player)
            # Saves registry to JSON
            self._save_to_json()


if __name__ == "__main__":
    pass
