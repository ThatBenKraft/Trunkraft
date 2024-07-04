"""
item registry that syncs to JSON file.
"""

import json
from collections import deque
from pathlib import Path
from typing import Any, Generator, Iterable

# Constants for json paths
DEFAULT_JSON_PATH = Path(__file__).parent / "databases/registry.json"


class Registry:
    """
    Active registry that syncs to a JSON file.
    """

    def __init__(
        self,
        path: Path = DEFAULT_JSON_PATH,
        max_length=None,
        load_existing: bool = True,
    ) -> None:
        """
        Active registry that syncs to a JOSN file.
        """
        self._path = path
        self._data: deque[str] = deque(maxlen=max_length) if max_length else deque()
        self.max_length = max_length
        # If file exists
        if self._path.exists() and load_existing:
            try:
                # Opens and returns data
                with open(self._path, "r") as file:
                    json_data = json.load(file)
                    # Checks for invalid data type
                    if not self.correct_format(json_data):
                        raise ValueError("Invalid data format in JSON file")
                    self._data: deque[str] = deque(json_data)
            # Handles decoding and other errors
            except json.JSONDecodeError:
                print(f"Error: Failed to decode JSON from {self._path}")
                self._data = deque()
            except (ValueError, IOError) as error:
                print(f"Error: {error}")
                self._data = deque()
        else:
            self._save_to_json()

    def correct_format(self, json_data: Any) -> bool:
        """
        Determines if JSON data is formatted correctly.
        """
        if isinstance(json_data, list):
            return all(isinstance(item, str) for item in json_data)
        return False

    def __contains__(self, item: str) -> bool:
        return item in self._data

    def contains_substring(self, substring: str) -> bool:
        return any(substring in item for item in list(self._data))

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Generator[str, Any, None]:
        for item in list(self._data):
            yield item

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
                json.dump(list(self._data), file, indent=4)
        # Handles file writing errors
        except IOError as error:
            print(f"Error: Failed to write to {self._path}: {error}")

    def add(self, item: str) -> None:
        """
        Adds item to JSON registry.
        """
        # Adds item
        self._data.append(item)
        # Saves registry to JSON
        self._save_to_json()

    def extend(self, items: Iterable[str]) -> None:
        """
        Adds multiple items to JSON registry.
        """
        # Adds items
        self._data.extend(items)
        # Saves registry to JSON
        self._save_to_json()

    def remove(self, item: str) -> None:
        """
        Removes item from JSON registry.
        """
        # If item is in registry:
        if item in self._data:
            # Removes item
            self._data.remove(item)
            # Saves registry to JSON
            self._save_to_json()

    def clear(self) -> None:
        """
        Clears all items from JSON registry.
        """
        self._data.clear()
        self._save_to_json()


if __name__ == "__main__":
    small_reg = Registry(Path(__file__).parent / "databases/testing.json", 2)

    small_reg.add("a")
    small_reg.add("b")
    print(small_reg)
    small_reg.add("c")
    print(small_reg)
