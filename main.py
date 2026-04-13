"""This file provides the driving logic for the backend management process."""

import sys
import mgmt_utils
import backend
import mgmt_io

def markdown_flow(path_name: str) -> int:
    """Flow for markdown files."""
    fm = mgmt_utils.load_frontmatter(path_name)
    doc_type = mgmt_io.doctype_message(fm)
    if not mgmt_io.verify_frontmatter(fm, doc_type):
        return 1
    mgmt_io.print_divider(20)
    db_manager = backend.DBManager(fm, path_name, doc_type)
    exists, existing_item = db_manager.exists_in_db()
    if exists:
        user_resp = mgmt_io.prompt_existing_document(db_manager, existing_item)
        return mgmt_utils.execute_existing_document(db_manager, existing_item, user_resp)
    else:
        user_resp = mgmt_io.prompt_new_document(db_manager)
        return mgmt_utils.execute_new_document(db_manager, user_resp)

def folder_flow(path_name: str) -> int:
    """Flow for pdf files."""
    raise NotImplementedError


def main() -> int:
    """Main function for the backend management process."""
    path_name = mgmt_io.get_input("Please provide a path to the file or folder you would like to add to your site:").strip('" ')

    if not mgmt_utils.is_pathname_valid(path_name):
        print("Invalid path provided.")
        return 1

    # check if it's a folder
    is_folder, error = mgmt_io.is_pathname_folder_message(path_name)
    if error is not None:
        print(error)
        return 1

    if is_folder:
        return folder_flow(path_name)
    else:
        return markdown_flow(path_name)

if __name__ == "__main__":
    sys.exit(main())
