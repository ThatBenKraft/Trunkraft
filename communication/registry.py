"""
Item registry that syncs to JSON file.
"""

import json
from collections import deque
from pathlib import Path
from typing import Any, Generator, Iterable

# Constants for JSON paths
DEFAULT_JSON_PATH = Path(__file__).parent / "databases/registry.json"


class Registry:
    """
    Active registry that syncs to a JSON file.
    """

    def __init__(
        self,
        path: Path = DEFAULT_JSON_PATH,
        max_length: int | None = None,
        load_existing: bool = True,
        data_type: type = deque,
    ) -> None:
        """
        Initializes registry at path, loading existing by default. Can be of
        any type compatible with JSON files.
        """
        self._path = path
        self.data_type = data_type
        self.max_length = max_length

        # Initialize the data structure
        self._data = data_type(maxlen=max_length) if data_type == deque else data_type()

        # Load existing data if file exists and load_existing is True
        if self._path.exists() and load_existing:
            try:
                with open(self._path, "r") as file:
                    json_data = json.load(file)
                    if self.correct_format(json_data):
                        if data_type == deque:
                            self._data = deque(json_data, maxlen=max_length)
                        elif data_type == list or data_type == list:
                            self._data = json_data
                    else:
                        raise ValueError("Invalid data format in JSON file")
            except json.JSONDecodeError:
                print(f"Error: Failed to decode JSON from {self._path}")
                self._data = data_type()
            except (ValueError, IOError) as error:
                print(f"Error: {error}")
                self._data = data_type()
        else:
            self._save_to_json()

    def correct_format(self, json_data: Any) -> bool:
        """
        Determines if JSON data is formatted correctly.
        """
        if self.data_type == deque or self.data_type == list:
            return isinstance(json_data, list)
        elif self.data_type == dict:
            return isinstance(json_data, dict)
        return False

    def __contains__(self, item: Any) -> bool:
        return item in list(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Generator[Any, Any, None]:
        for item in list(self._data):
            yield item

    def items(self) -> Generator[tuple, Any, None]:
        """
        Returns an iterator over the (key, value) pairs of the registry.
        """
        if isinstance(self._data, dict):
            for key, value in self._data.items():
                yield key, value
        else:
            raise TypeError("Items() method is only supported for dictionaries.")

    def __str__(self) -> str:
        return str(self._data)

    def _save_to_json(self) -> None:
        """
        Saves data to JSON file.
        """
        try:
            with open(self._path, "w") as file:
                # Acquires data in correct format
                data = self._data if isinstance(self._data, dict) else list(self._data)
                # Writes data to JSON file
                json.dump(data, file, indent=4)
        except IOError as error:
            print(f"Error: Failed to write to {self._path}: {error}")

    def add(self, item: Any) -> None:
        """
        Adds an item to the registry.
        """
        if isinstance(self._data, (deque, list)):
            self._data.append(item)
        elif isinstance(self._data, dict):
            # Adds a key with a None value
            self._data[item] = None
        self._save_to_json()

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Set item in the registry using `registry[key] = value`.
        """
        # Throws error if not a dictionary
        if isinstance(self._data, (dict)):
            self._data[key] = value
            self._save_to_json()
        else:
            raise TypeError(f"Registry is not of type dict: {type(self._data)}")

    def __getitem__(self, key: Any) -> None:
        """
        Set item in the registry using `registry[key] = value`.
        """
        # Throws error if not a dictionary
        if isinstance(self._data, (dict)):
            return self._data[key]
        else:
            raise TypeError(f"Registry is not of type dict: {type(self._data)}")

    def extend(self, items: Iterable[Any]) -> None:
        """
        Adds multiple items to the registry.
        """
        if isinstance(self._data, (deque, list)):
            self._data.extend(items)
        elif isinstance(self._data, dict):
            # Adds keys with None values
            for item in items:
                self._data[item] = None
        self._save_to_json()

    def remove(self, item: Any) -> None:
        """
        Removes an item from the registry.
        """
        if item in self._data:
            if isinstance(self._data, (deque, list)):
                self._data.remove(item)
            elif isinstance(self._data, (dict)):
                self._data.pop(item)
            self._save_to_json()

    def clear(self) -> None:
        """
        Clears all items from the registry.
        """
        self._data.clear()
        self._save_to_json()


if __name__ == "__main__":
    small_reg = Registry(
        Path(__file__).parent / "databases/testing.json", max_length=3, data_type=deque
    )

    small_reg.add("a")
    small_reg.add("b")
    print(small_reg)
    small_reg.add("c")
    print(small_reg)

    big_registry = Registry(
        Path(__file__).parent / "databases/testing_big.json", load_existing=False
    )

    big_registry.add({1: 2})
    big_registry.add(["a", "b"])

    print(big_registry)
