"""This module provides utility functions for the backend management process."""

import os
import constants

ERROR_INVALID_NAME = 123

def is_pathname_folder(pathname: str) -> bool:
    """Returns `True` if the passed pathname is a folder; `False` otherwise."""
    return os.path.isdir(pathname)

def is_pathname_valid(pathname: str) -> bool:
    """Returns `True` if the passed pathname is valid; `False` otherwise."""
    if not isinstance(pathname, str) or not pathname:
        return False
    normalized = os.path.normpath(pathname.strip('"'))
    return os.path.exists(normalized)

def path_exists(pathname: str) -> bool:
    '''
    True if passed pathname exists, False otherwise/
    '''
    try:
        return is_pathname_valid(pathname) and (os.path.exists(pathname))
    except OSError:
        return False

def get_file_ext(pathname: str) -> str:
    """Returns the file extension of the passed pathname."""
    return os.path.splitext(pathname)[1]

def is_valid_frontmatter(
        frontmatter: dict,
        typekey: str,
        keysets: dict[constants.DocType, set[constants.FrontMatterKey]]
    ) -> tuple[bool, str]:
    """Returns True if provided frontmatter has expected keys and values"""
    keys = set(frontmatter.keys())

    if not typekey in keys:
        return False, f"missing required key: {typekey}"

    required_keys = keysets[frontmatter[typekey]]
    for key in required_keys:
        if not key in keys:
            return False, f"missing required key: {key}"

    return True, ""

def print_frontmatter(
        frontmatter: dict,
        required_keys: set[constants.FrontMatterKey],
        optional_keys: set[constants.FrontMatterKey]
    ):
    """Prints frontmatter to console."""
    for key in required_keys:
        print(f"{key.value}: {frontmatter[key]}")

    for key in optional_keys:
        if key in frontmatter:
            print(f"{key.value}: {frontmatter[key]}")
