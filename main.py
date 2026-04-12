"""This file provides the driving logic for the backend management process."""

import sys

import frontmatter
import mgmt_utils
import backend
import constants

def markdown_flow(path_name: str) -> int:
    """Flow for markdown files."""
    with open(path_name, encoding="utf-8") as f:
        fm = frontmatter.load(f)
        valid, error = mgmt_utils.is_valid_frontmatter(
            fm,
            constants.FrontMatterKey.TYPEKEY,
            constants.FrontMatterKeySets
        )
        if not valid:
            print("md file contains invalid frontmatter: ", error)
            return 1
    doc_type = fm[constants.FrontMatterKey.TYPEKEY]
    print("-" * 20)
    print(f"Document appears to be a {doc_type} with...")
    mgmt_utils.print_frontmatter(
        fm,
        constants.FrontMatterKeySets[doc_type],
        constants.FrontMatterOptional
    )
    correct_resp = input("Is this correct? (y/n) > ")
    match(correct_resp):
        case "y":
            pass
        case "n":
            print("Please correct the frontmatter. Aborting.")
            return 1
        case _:
            print("Invalid response provided.")
            return 1
    print("-" * 20)
    db_manager = backend.DBManager(fm, path_name, doc_type)
    exists = db_manager.exists_in_db()
    if exists:
        print("File already exists in database. What would you like to do?")
        print("1. Replace existing entry with this one.")
        print("2. Delete existing entry.")
        print("3. Change publication status of existing entry.")
        change_resp = input("> ")
        match(change_resp):
            case "1":
                db_manager.write_md_to_db()
            case "2":
                db_manager.delete_md_from_db()
            case "3":
                stat_bool = db_manager.get_md_status()
                status, new_status = ["published", "unpublished"] if stat_bool else ["unpublished", "published"]
                print(f"Current status: {status}")
                print(f"Would you like to change it to {new_status}?")
                status_resp = input("(y/n) > ")
                match(status_resp):
                    case "y":
                        db_manager.change_md_status()
                    case "n":
                        return 0
                    case _:
                        print("Invalid response provided.")
                        return 1
            case _:
                print("Invalid response provided.")
                return 1
    else:
        print("Would you like to add this file to the database?")
        add_resp = input("(y/n) > ")
        match(add_resp):
            case "y":
                db_manager.write_md_to_db()
            case "n":
                return 0
            case _:
                print("Invalid response provided.")
                return 1
    return 0

def folder_flow(path_name: str) -> int:
    """Flow for pdf files."""
    pass

def main() -> int:
    """Main function for the backend management process."""
    print("Please provide a path to the file or folder you would like to add to your site:")
    path_name = input("> ").strip('" ')

    # validate path
    if not mgmt_utils.is_pathname_valid(path_name):
        print("Invalid path provided.")
        return 1

    # check if it's a folder
    if mgmt_utils.is_pathname_folder(path_name):
        print("Folder provided. This will be treated as either a story or an adventure module.")
        folder_flow(path_name)
        return 1
    else:
        print("File provided. This will be treated as a story chapter, article, or review.")
        ext = mgmt_utils.get_file_ext(path_name)
        match ext:
            case ".md":
                print("Markdown file detected. Scanning for frontmatter...")
                return markdown_flow(path_name)
            case _:
                print("Unsupported file type.")
                return 1

if __name__ == "__main__":
    sys.exit(main())
