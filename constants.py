"""Constants for the backend management process."""

import string
from pydantic import BaseModel, Field
from enum import Enum
from abc import ABC, abstractmethod
from typing import Literal, Annotated


class DocType(str, Enum):
    """Enum for document types."""

    ADVENTURE = "adventure"
    ARTICLE = "article"
    REVIEW = "review"
    STORY = "story"
    STORYCHAPTER = "story_chapter"


DocTypeToS3Folder = {
    DocType.ADVENTURE: "adventures",
    DocType.ARTICLE: "articles",
    DocType.REVIEW: "reviews",
    DocType.STORY: "story_pages",
    DocType.STORYCHAPTER: "story_chapters",
}


class DBField(str, Enum):
    """Enum for DynamoDB fields."""

    PK = "header"
    SK = "id"
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
    AUTHORS = "authors"


class FrontMatterBase(BaseModel, ABC):
    """Base class for frontmatter models."""

    authors: list[str] = Field(default=[], alias=FrontMatterKey.AUTHORS)
    tags: list[str] = Field(default=[], alias=DBField.TAGS)

    @abstractmethod
    def get_sort_key(self) -> str:
        raise NotImplementedError

    class Config:
        extra = "forbid"
        anystr_strip_whitespace = True
        allow_mutation = False


class Adventure(FrontMatterBase):
    type: Literal[DocType.ADVENTURE]
    title: str = Field(alias=FrontMatterKey.TITLE)

    def get_sort_key(self) -> str:
        return get_adventure_sk(self.dict(by_alias=True))


class Article(FrontMatterBase):
    type: Literal[DocType.ARTICLE]
    category: str = Field(alias=FrontMatterKey.CATEGORY)
    title: str = Field(alias=FrontMatterKey.TITLE)

    def get_sort_key(self) -> str:
        return get_article_sk(self.dict(by_alias=True))


class Review(FrontMatterBase):
    type: Literal[DocType.REVIEW]
    subject: str = Field(alias=FrontMatterKey.SUBJECT)
    title: str = Field(alias=FrontMatterKey.TITLE)

    def get_sort_key(self) -> str:
        return get_review_sk(self.dict(by_alias=True))


class Story(FrontMatterBase):
    type: Literal[DocType.STORY]
    storyTitle: str = Field(alias=FrontMatterKey.STORYTITLE)

    def get_sort_key(self) -> str:
        return get_story_sk(self.dict(by_alias=True))


class StoryChapter(FrontMatterBase):
    type: Literal[DocType.STORYCHAPTER]
    storyTitle: str = Field(alias=FrontMatterKey.STORYTITLE)
    chapterNumber: int = Field(alias=FrontMatterKey.CHAPTERNUMBER)
    chapterTitle: str = Field(alias=FrontMatterKey.CHAPTERTITLE)

    def get_sort_key(self) -> str:
        return get_story_chapter_sk(self.dict(by_alias=True))


FrontMatter = Annotated[
    Adventure | Article | Review | Story | StoryChapter,
    Field(discriminator="type"),
]


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
    chapter_number = str(chapter_number).zfill(3)
    return f"TITLE#{story_title}#CHAPTER#{chapter_number}"


def normalize_string(s: str) -> str:
    """Remove punctuation and replace spaces with hyphens and converts to lowercase."""

    s = s.translate(str.maketrans("", "", string.punctuation))
    return s.replace(" ", "-").lower()
