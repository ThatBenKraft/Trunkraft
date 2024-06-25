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
        # If file exists
        if self._path.exists():
            # Opens and returns data
            with open(self._path, "r") as file:
                self._data: list[str] = json.load(file)
        else:
            # Creates file
            self._data = self._save([])

    def __contains__(self, player: str) -> bool:
        return player in self._data

    def __iter__(self) -> Generator[str, Any, None]:
        for player in self._data:
            yield player

    def __str__(self) -> str:
        return ", ".join(self._data)

    def _save(self, players: list[str]) -> list[str]:
        """
        Saves data to JSON file.
        """
        with open(self._path, "w") as file:
            json.dump(players, file, indent=4)
        # Returns with parameter
        return players

    def add(self, player: str) -> None:
        """
        Adds player to JSON registry.
        """
        # If player not already in registry:
        if player not in self._data:
            # Adds player
            self._data.append(player)
            # Saves registry to JSON
            self._save(self._data)

    def remove(self, player: str) -> None:
        """
        Removes player from JSON registry.
        """
        # If player is in registry:
        if player in self._data:
            # Removes player
            self._data.remove(player)
            # Saves registry to JSON
            self._save(self._data)


if __name__ == "__main__":
    pass
