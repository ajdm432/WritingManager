"""This module provides utility functions for the backend management process."""

import os
import constants
import frontmatter

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

def load_frontmatter(pathname: str) -> dict:
    """Loads frontmatter from a markdown file."""
    with open(pathname, encoding="utf-8") as f:
        fm = frontmatter.load(f)
        valid, error = is_valid_frontmatter(
            fm,
            constants.FrontMatterKey.TYPEKEY,
            constants.FrontMatterKeyLists
        )
        if not valid:
            raise ValueError("md file contains invalid frontmatter: ", error)
    return fm

def execute_existing_document(db_manager, existing_item, selection) -> int:
    """Runs db operation based on user input"""
    match(selection):
        case "1":
            db_manager.write_md_to_db(existing_item)
        case "2":
            db_manager.delete_md_from_db(existing_item)
        case "3":
            stat_bool = db_manager.get_md_status()
            status, new_status = ["published", "unpublished"] if stat_bool else ["unpublished", "published"]
            print(f"Current status: {status}")
            print(f"Would you like to change it to {new_status}?")
            status_resp = input("(y/n) > ")
            match(status_resp):
                case "y":
                    db_manager.change_md_status(existing_item)
                case "n":
                    pass
                case _:
                    print("Invalid response provided.")
                    return 1
        case _:
            print("Invalid response provided.")
            return 1
    return 0

def execute_new_document(db_manager, selection) -> int:
    """Runs db operation based on user input"""
    match(selection):
        case "y":
            db_manager.write_md_to_db(None)
        case "n":
            pass
        case _:
            print("Invalid response provided.")
            return 1
    return 0
