"""I/O functions for the backend management process."""

import mgmt_utils
import constants


def get_input(s: str) -> str:
    """Prompts the user for input."""
    print(s)
    return input("> ")


def is_pathname_folder_message(pathname: str) -> bool:
    """Returns `True` if the passed pathname is a folder; `False` otherwise."""
    if mgmt_utils.is_pathname_folder(pathname):
        print(
            "Folder provided. This will be treated as either a story or an adventure module."
        )
        return True
    else:
        print(
            "File provided. This will be treated as a story chapter, article, or review."
        )
        return False


def is_markdown_file(pathname: str) -> bool:
    """Returns `True` if the passed pathname is a markdown file; `False` otherwise."""
    return pathname.endswith(".md")


def is_pdf_file(pathname: str) -> bool:
    """Returns `True` if the passed pathname is a pdf file; `False` otherwise."""
    return pathname.endswith(".pdf")


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
        constants.FrontMatterOptional,
    )
    correct_resp = input("Is this correct? (y/n) > ")
    match correct_resp:
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


def prompt_existing_document() -> str:
    """Prompts the user to handle an existing entry in the database."""
    print("File already exists in database. What would you like to do?")
    print("1. Replace existing entry with this one.")
    print("2. Delete existing entry.")
    print("3. Change publication status of existing entry.")
    return input("> ")


def prompt_new_document() -> str:
    """Prompts the user to handle a new entry in the database."""
    print("Would you like to add this file to the database?")
    return input("(y/n) > ")
