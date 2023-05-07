from os import path
from pickle import load, dump
from typing import Any


def readBinaryFile(filePath: str) -> Any | None:
    """
    :param filePath: Path to the binary file.
    :return: Any data or None.
    Returns the data stored in the binary file.
    """
    with open(filePath, "rb") as file:
        data = load(file)
    return data


def saveToBinaryFile(filePath: str, data: Any | None) -> None:
    """
    :param filePath: Path to the binary file.
    :param data: Data to be saved.
    Saves input data in the desired binary file.
    """
    with open(filePath, "wb") as file:
        dump(data, file)


def loadBinaryFile(filePath: str) -> Any | None:
    """
    :param filePath: Path to binary file.
    :return: Any data or None.
    Loads binary file and returns the data stored in it. If the file doesn't exist, creates a new one at specified path
    and returns None.
    """
    if path.isfile(filePath):
        return readBinaryFile(filePath)
    else:
        saveToBinaryFile(filePath, None)
        return None
