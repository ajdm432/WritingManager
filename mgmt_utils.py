"""This module provides utility functions for the backend management process."""

import os
import constants
import frontmatter
import zipfile
from typing import Tuple
from pydantic import TypeAdapter

FRONTMATTER_ADAPTER = TypeAdapter(constants.FrontMatter)


def is_pathname_folder(pathname: str) -> bool:
    """Returns `True` if the passed pathname is a folder; `False` otherwise."""
    return os.path.isdir(pathname)


def path_exists(pathname: str) -> bool:
    """
    True if passed pathname exists, False otherwise/
    """
    if not isinstance(pathname, str) or not pathname:
        return False
    try:
        pathname = os.path.normpath(pathname.strip('"'))
        return os.path.exists(pathname)
    except OSError:
        return False


def get_file_ext(pathname: str) -> str:
    """Returns the file extension of the passed pathname."""
    return os.path.splitext(pathname)[1]


def print_frontmatter(
    frontmatter: dict,
):
    """Prints frontmatter to console."""
    for key, value in frontmatter.items():
        print(f"{key}: {value}\n")


def load_frontmatter(pathname: str) -> constants.FrontMatter:
    """Loads frontmatter from a markdown file."""
    with open(pathname, encoding="utf-8") as f:
        fm_raw = frontmatter.load(f)
        # use pydantic to validate
        fm = FRONTMATTER_ADAPTER.validate_python(fm_raw)
    return fm


def execute_existing_document(
    db_manager, existing_item, selection
) -> Tuple[int, str | None]:
    """Runs db operation based on user input"""
    match selection:
        case "1":
            stat_bool = db_manager.get_md_status()
            db_manager.write_md_to_db(existing_item, publish=stat_bool)
            if db_manager.doc_type == constants.DocType.STORY:
                db_manager.write_story_to_s3()
        case "2":
            if db_manager.doc_type == constants.DocType.STORY:
                db_manager.delete_story_from_s3()
            db_manager.delete_md_from_db(existing_item)
        case "3":
            stat_bool = db_manager.get_md_status()
            new_status = "unpublished" if stat_bool else "published"
            return 0, new_status
        case _:
            print("Invalid response provided.")
            return 1, None
    return 0, None


def execute_new_document(db_manager, selection) -> int:
    """Runs db operation based on user input"""
    match selection:
        case "y":
            db_manager.write_md_to_db(None)
        case "n":
            pass
        case _:
            print("Invalid response provided.")
            return 1
    return 0


def find_yaml(path_name: str, folder: bool) -> str:
    """Finds the yaml file with frontmatter in the provided folder."""
    if folder:
        dir_name = path_name
    else:
        dir_name = os.path.dirname(path_name)

    yaml_files = [
        f for f in os.listdir(dir_name) if (f.endswith(".yaml") or f.endswith(".yml"))
    ]
    if len(yaml_files) != 1:
        return None
    return os.path.join(dir_name, yaml_files[0])


def zip_folder(path_name: str, yaml_path: str) -> str:
    """Creates a zip file of the provided folder, leaving out the yaml file, in the tmp directory."""
    temp = os.path.join(os.getcwd(), "tmp")
    os.makedirs(temp, exists_ok=True)
    zip_path = os.path.join(temp, os.path.basename(path_name) + ".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(path_name):
            for file in files:
                if file == os.path.basename(yaml_path):
                    continue
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, path_name)
                zipf.write(full_path, relative_path)

    return zip_path


def clean_zip(zip_path: str) -> None:
    """Removes the zip file and its parent directory if it is empty."""
    os.remove(zip_path)
    if os.listdir(os.path.dirname(zip_path)):
        return
    os.rmdir(os.path.dirname(zip_path))


def validate_story_folder(src_path: str) -> Tuple[list[str], list[str]]:
    expected = [
        "description",
        "theme",
        "background",
        "cover",
        "logo",
        "banner",
    ]
    found = []
    for file in os.listdir(src_path):
        if file == "description.md":
            found.append(file.split(".")[0])
        elif file == "theme.css":
            found.append(file.split(".")[0])
        elif file in ["background.jpg", "background.png", "background.jpeg"]:
            found.append(file.split(".")[0])
        elif file in ["cover.jpg", "cover.png", "cover.jpeg"]:
            found.append(file.split(".")[0])
        elif file in ["logo.png", "logo.jpg", "logo.jpeg", "logo.svg", "logo.ico"]:
            found.append(file.split(".")[0])
        elif file in ["banner.jpg", "banner.png", "banner.jpeg"]:
            found.append(file.split(".")[0])
        else:
            msg = f"Unsupported file type: {file}. Must be one of: {expected}"
            print(msg)
            raise ValueError(msg)
    missing = list(set(expected) - set(found))
    return found, missing
