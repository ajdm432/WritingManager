"""Constants for the backend management process."""

import sys
import string
from enum import Enum

DB_TIMEOUT = 15
DB_RETRIES = 5

class DocType(str, Enum):
    """Enum for document types."""
    ADVENTURE = "adventure"
    ARTICLE = "article"
    REVIEW = "review"
    STORY = "story"
    STORYCHAPTER = "story_chapter"

class DBField(str, Enum):
    """Enum for DynamoDB fields."""
    PK = "header"
    SK = "id"
    AUTHOR = "author"
    PUBLISHED = "is_published"
    TAGS = "tags"
    S3_PATH = "s3_path"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"

class FrontMatterKey(str, Enum):
    """Enum for frontmatter keys. These correspond to parts of PK and SK in the database."""
    TYPEKEY = "type"
    CATEGORY = "category"
    SUBJECT = "subject"
    STORYTITLE = "story_title"
    CHAPTERNUMBER = "chapter_number"
    CHAPTERTITLE = "chapter_title"
    TITLE = "title"

FrontMatterKeySets: dict[DocType, set[FrontMatterKey | DBField]] = {
    DocType.ADVENTURE: [
        FrontMatterKey.TITLE
        # TODO handle remaining adventure frontmatter
    ],
    DocType.ARTICLE: [
        FrontMatterKey.CATEGORY,
        FrontMatterKey.TITLE
    ],
    DocType.REVIEW: [
        FrontMatterKey.SUBJECT,
        FrontMatterKey.TITLE
    ],
    DocType.STORY: [
        FrontMatterKey.STORYTITLE
        # TODO handle remaining story frontmatter
    ],
    DocType.STORYCHAPTER: [
        FrontMatterKey.STORYTITLE,
        FrontMatterKey.CHAPTERNUMBER,
        FrontMatterKey.CHAPTERTITLE
    ]
}

FrontMatterOptional: set[DBField] = {
    DBField.AUTHOR,
    DBField.TAGS
}

# Helpers for formatting partition keys
def get_section_pk(section_name: str) -> str:
    """Returns the primary key for a section."""
    return f"SECTION#{section_name}"

def get_meta_pk(meta_name: str) -> str:
    """Returns the primary key for a meta."""
    return f"META#{meta_name}"

def get_tag_pk(tag_name: str) -> str:
    """Returns the primary key for a tag."""
    return f"TAG#{tag_name}"

# Helpers for formatting sort keys
def get_adventure_sk(frontmatter: dict) -> str:
    """Returns the sort key for an adventure."""
    # TODO
    pass

def get_article_sk(frontmatter: dict) -> str:
    """Returns the sort key for an article."""
    category = normalize_string(frontmatter[FrontMatterKey.CATEGORY])
    title = normalize_string(frontmatter[FrontMatterKey.TITLE])
    return f"CATEGORY#{category}#TITLE#{title}"

def get_review_sk(frontmatter: dict) -> str:
    """Returns the sort key for a review."""
    review_subject = normalize_string(frontmatter[FrontMatterKey.SUBJECT])
    review_title = normalize_string(frontmatter[FrontMatterKey.TITLE])
    return f"REVIEW#{review_subject}#TITLE#{review_title}"

def get_story_sk(frontmatter: dict) -> str:
    """Returns the sort key for a story."""
    # TODO
    pass

def get_story_chapter_sk(frontmatter: dict) -> str:
    """Returns the sort key for a story."""
    story_title = normalize_string(frontmatter[FrontMatterKey.STORYTITLE])
    chapter_number = frontmatter[FrontMatterKey.CHAPTERNUMBER]
    try:
        chapter_number = int(chapter_number)
    except ValueError:
        print("Chapter number must be an integer.")
        sys.exit(1)
    chapter_number = str(chapter_number).zfill(3)
    return f"TITLE#{story_title}#CHAPTER#{chapter_number}"

def normalize_string(s: str) -> str:
    """Remove punctuation and title spaces with hyphens and converts to lowercase."""

    s = s.translate(str.maketrans('', '', string.punctuation))
    return s.replace(" ", "-").lower()

DocTypeToSK = {
    DocType.ADVENTURE: get_adventure_sk,
    DocType.ARTICLE: get_article_sk,
    DocType.REVIEW: get_review_sk,
    DocType.STORY: get_story_sk,
    DocType.STORYCHAPTER: get_story_chapter_sk
}

DocTypeToS3Folder = {
    DocType.ADVENTURE: "adventures",
    DocType.ARTICLE: "articles",
    DocType.REVIEW: "reviews",
    DocType.STORY: "story_pages",
    DocType.STORYCHAPTER: "story_chapters"
}
