from os import path
from pickle import load, dump
from typing import Any


def readBinaryFile(filePath: str) -> Any | None:
    """
    :param filePath: Path to binary file.
    Returns Unix time saved in binary file, rounded to seconds.
    """
    with open(filePath, "rb") as file:
        resetTime = load(file)
    return resetTime


def saveToBinaryFile(filePath: str, resetTime: Any | None) -> None:
    """
    :param filePath: Path to binary file.
    :param resetTime: Unix timestamp rounded to seconds.
    Saves Unix time in binary file.
    """
    with open(filePath, "wb") as file:
        dump(resetTime, file)


def loadBinaryFile(filePath: str) -> Any | None:
    """
    :param filePath: Path to binary file.
    Loads binary file and returns Unix time stored in it. If the file doesn't exist, creates a new one at specified path
    and returns current Unix timestamp as the default value, rounded to seconds.
    """
    if path.isfile(filePath):
        return readBinaryFile(filePath)
    else:
        saveToBinaryFile(filePath, None)
        return None
