"""This file provides the driving logic for the backend management process."""

import sys
import mgmt_utils
import backend
import mgmt_io
import constants
from typing import Tuple


def story_flow(fm: constants.FrontMatter, path_name: str, doc_type: str) -> int:
    """Flow for story folders."""
    found, missing = mgmt_utils.validate_story_folder(path_name)
    resp = mgmt_io.prompt_story_folder(found, missing)
    if resp != "y":
        print("Aborting upload.")
        return 1
    db_flow(fm, path_name, doc_type)


def fm_flow(path_name: str) -> Tuple[constants.FrontMatter, str]:
    """Flow for frontmatter files."""
    fm = mgmt_utils.load_frontmatter(path_name)
    doc_type = mgmt_io.doctype_message(fm.dict(by_alias=True))
    if not mgmt_io.verify_frontmatter(fm.dict(by_alias=True), doc_type):
        return None, None
    mgmt_io.print_divider(20)
    return fm, doc_type


def db_flow(fm: constants.FrontMatter, path_name: str, doc_type: str) -> int:
    """Flow for database operations."""
    db_manager = backend.DBManager(fm, path_name, doc_type)
    exists, existing_item = db_manager.exists_in_db()
    if exists:
        user_resp = mgmt_io.prompt_existing_document()
        return mgmt_utils.execute_existing_document(
            db_manager, existing_item, user_resp
        )
    else:
        user_resp = mgmt_io.prompt_new_document()
        return mgmt_utils.execute_new_document(db_manager, user_resp)


def folder_flow(path_name: str) -> int:
    """Flow for pdf files."""
    fm_path = mgmt_utils.find_yaml(path_name, True)
    if fm_path is None:
        print(
            "Could not find yaml file with frontmatter in the provided folder.\nPlease make sure your yaml file is in the provided folder and that there is only one yaml file in the folder."
        )
        return 1
    fm, doc_type = fm_flow(path_name)
    if fm is None:
        return 1
    # before we do this, check what RPG systems are already defined on the backend. If this one isn't, display the current list to the user, as well as the current system for this upload.
    # they may see that a different name for their desired system already exists, and they can choose to replace it before uploading.
    tmp_manager = backend.DBManager(fm, path_name, doc_type)
    rpg_systems = tmp_manager.get_rpg_systems()
    if fm.system not in rpg_systems:
        resp = mgmt_io.prompt_rpg_system(fm.system, rpg_systems)
        if resp != "y":
            print("Aborting upload.")
            return 1
    zip_path = mgmt_utils.zip_folder(path_name, fm_path)
    db_flow(fm, zip_path, doc_type)
    mgmt_utils.clean_zip(zip_path)


def markdown_flow(path_name: str) -> int:
    """Flow for markdown files."""
    fm, doc_type = fm_flow(path_name)
    if fm is None:
        return 1
    if doc_type == constants.DocType.STORY:
        return story_flow(fm, path_name, doc_type)
    else:
        return db_flow(fm, path_name, doc_type)


def pdf_flow(path_name: str) -> int:
    """Flow for pdf files."""
    fm_path = mgmt_utils.find_yaml(path_name, False)
    if fm_path is None:
        print(
            "Could not find yaml file with frontmatter in the same directory as the pdf.\nPlease make sure your yaml file is in the same directory as the pdf and has the same name."
        )
        return 1
    fm, doc_type = fm_flow(path_name)
    if fm is None:
        return 1
    db_flow(fm, path_name, doc_type)


def main() -> int:
    """Main function for the backend management process."""
    path_name = mgmt_io.get_input(
        "Please provide a path to the file or folder you would like to add to your site:"
    ).strip('" ')

    if not mgmt_utils.is_pathname_valid(path_name):
        print("Invalid path provided.")
        return 1

    # check if it's a folder
    is_folder = mgmt_io.is_pathname_folder_message(path_name)

    if is_folder:
        # upload full folder. Must contain a yaml file with frontmatter
        return folder_flow(path_name)
    elif mgmt_io.is_markdown_file(path_name):
        # upload markdown file that contains yaml frontmatter
        print("Markdown file detected. Scanning for frontmatter...")
        return markdown_flow(path_name)
    elif mgmt_io.is_pdf_file(path_name):
        # upload pdf file. Yaml file with frontmatter must exist in the same directory, with the same name
        print("PDF file detected. Scanning for frontmatter...")
        return pdf_flow(path_name)
    else:
        print("Unsupported file type.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
