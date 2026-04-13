"""I/O functions for the backend management process."""

import mgmt_utils
import constants

def get_input(s: str) -> str:
    """Prompts the user for input."""
    print(s)
    return input("> ")

def is_pathname_folder_message(pathname: str) -> tuple[bool, str]:
    """Returns `True` if the passed pathname is a folder; `False` otherwise."""
    if mgmt_utils.is_pathname_folder(pathname):
        print("Folder provided. This will be treated as either a story or an adventure module.")
        return True, None
    else:
        print("File provided. This will be treated as a story chapter, article, or review.")
        ext = mgmt_utils.get_file_ext(pathname)
        match ext:
            case ".md":
                print("Markdown file detected. Scanning for frontmatter...")
                return False, None
            case _:
                return False, "Unsupported file type."

def doctype_message(frontmatter: dict) -> str:
    """Prints and returns the document type."""
    doc_type = frontmatter[constants.FrontMatterKey.TYPEKEY]
    print("-" * 20)
    print(f"Document appears to be a {doc_type} with...")
    return doc_type

def verify_frontmatter(frontmatter: dict, doctype: str) -> bool:
    """Prompts the user to verify frontmatter."""
    mgmt_utils.print_frontmatter(
        frontmatter,
        constants.FrontMatterKeyLists[doctype],
        constants.FrontMatterOptional
    )
    correct_resp = input("Is this correct? (y/n) > ")
    match(correct_resp):
        case "y":
            return True
        case "n":
            print("Please correct the frontmatter. Aborting.")
            return False
        case _:
            print("Invalid response provided.")
            return False

def print_divider(size: int) -> None:
    """Prints a divider."""
    print("-" * size)

def prompt_existing_document(db_manager, existing_item) -> str:
    """Prompts the user to handle an existing entry in the database."""
    print("File already exists in database. What would you like to do?")
    print("1. Replace existing entry with this one.")
    print("2. Delete existing entry.")
    print("3. Change publication status of existing entry.")
    return input("> ")
    

def prompt_new_document(db_manager) -> str:
    """Prompts the user to handle a new entry in the database."""
    print("Would you like to add this file to the database?")
    return input("(y/n) > ")
    
