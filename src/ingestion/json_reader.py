import json
from pathlib import Path
from typing import Any


class JsonReaderError(Exception):
    """Raised when a JSON file cannot be read or parsed."""

    pass


def read_json(file_path: Path) -> dict[str, Any]:
    """
    Read a JSON file and return its contents as a Python dictionary.

    Parameters
    ----------
    file_path:
        Path to the JSON file.

    Returns
    -------
    dict[str, Any]
        Parsed JSON data.

    Raises
    ------
    JsonReaderError
        If the file does not exist, cannot be read,
        contains invalid JSON, or does not contain
        a JSON object at the root.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise JsonReaderError(
            f"JSON file does not exist: {file_path}"
        )

    if not file_path.is_file():
        raise JsonReaderError(
            f"Path is not a file: {file_path}"
        )

    try:
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

    except OSError as exc:
        raise JsonReaderError(
            f"Unable to read JSON file: {file_path}"
        ) from exc

    except json.JSONDecodeError as exc:
        raise JsonReaderError(
            f"Invalid JSON in file: {file_path}"
        ) from exc

    if not isinstance(data, dict):
        raise JsonReaderError(
            f"Expected JSON object at root of file: {file_path}"
        )

    return data