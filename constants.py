"""Constants for the backend management process."""

import string
from pydantic import BaseModel, Field, ConfigDict
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
    DocType.STORY: "themes",
    DocType.STORYCHAPTER: "chapters",
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
    RPGSYSTEM = "system"


class FrontMatterBase(BaseModel, ABC):
    """Base class for frontmatter models."""

    authors: list[str] = Field(alias=FrontMatterKey.AUTHORS.value)
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)

    @abstractmethod
    def get_sort_key(self) -> str:
        raise NotImplementedError


class Adventure(FrontMatterBase):
    type: Literal[DocType.ADVENTURE.value]
    title: str = Field(alias=FrontMatterKey.TITLE.value)
    system: str = Field(alias=FrontMatterKey.RPGSYSTEM.value)
    tags: list[str] = Field(alias=DBField.TAGS.value)

    def get_sort_key(self) -> str:
        return get_adventure_sk(self.model_dump(by_alias=True))

    def get_s3_key(self) -> str:
        return get_adventure_s3_key(self.model_dump(by_alias=True))


class Article(FrontMatterBase):
    type: Literal[DocType.ARTICLE.value]
    category: str = Field(alias=FrontMatterKey.CATEGORY.value)
    title: str = Field(alias=FrontMatterKey.TITLE.value)
    tags: list[str] = Field(alias=DBField.TAGS.value)

    def get_sort_key(self) -> str:
        return get_article_sk(self.model_dump(by_alias=True))

    def get_s3_key(self) -> str:
        return get_article_s3_key(self.model_dump(by_alias=True))


class Review(FrontMatterBase):
    type: Literal[DocType.REVIEW.value]
    subject: str = Field(alias=FrontMatterKey.SUBJECT.value)
    title: str = Field(alias=FrontMatterKey.TITLE.value)
    tags: list[str] = Field(alias=DBField.TAGS.value)

    def get_sort_key(self) -> str:
        return get_review_sk(self.model_dump(by_alias=True))

    def get_s3_key(self) -> str:
        return get_review_s3_key(self.model_dump(by_alias=True))


class Story(FrontMatterBase):
    type: Literal[DocType.STORY.value]
    storyTitle: str = Field(alias=FrontMatterKey.STORYTITLE.value)
    tags: list[str] = Field(alias=DBField.TAGS.value)

    def get_sort_key(self) -> str:
        return get_story_sk(self.model_dump(by_alias=True))

    def get_s3_key(self) -> str:
        return get_story_s3_key(self.model_dump(by_alias=True))


class StoryChapter(FrontMatterBase):
    type: Literal[DocType.STORYCHAPTER.value]
    storyTitle: str = Field(alias=FrontMatterKey.STORYTITLE.value)
    chapterNumber: int = Field(alias=FrontMatterKey.CHAPTERNUMBER.value)
    chapterTitle: str = Field(alias=FrontMatterKey.CHAPTERTITLE.value)

    def get_sort_key(self) -> str:
        return get_story_chapter_sk(self.model_dump(by_alias=True))

    def get_s3_key(self) -> str:
        return get_story_chapter_s3_key(self.model_dump(by_alias=True))


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
    title = normalize_string(frontmatter[FrontMatterKey.TITLE])
    system = normalize_string(frontmatter[FrontMatterKey.RPGSYSTEM])
    # TODO track system as a meta field
    return f"RPGSYSTEM#{system}#TITLE#{title}"


def get_adventure_s3_key(frontmatter: dict) -> str:
    return f"{DocTypeToS3Folder[DocType.ADVENTURE]}/{normalize_string(frontmatter[FrontMatterKey.TITLE])}"


def get_article_sk(frontmatter: dict) -> str:
    """Returns the sort key for an article."""
    category = normalize_string(frontmatter[FrontMatterKey.CATEGORY])
    title = normalize_string(frontmatter[FrontMatterKey.TITLE])
    return f"CATEGORY#{category}#TITLE#{title}"


def get_article_s3_key(frontmatter: dict) -> str:
    return f"{DocTypeToS3Folder[DocType.ARTICLE]}/{normalize_string(frontmatter[FrontMatterKey.CATEGORY])}/{normalize_string(frontmatter[FrontMatterKey.TITLE])}"


def get_review_sk(frontmatter: dict) -> str:
    """Returns the sort key for a review."""
    review_subject = normalize_string(frontmatter[FrontMatterKey.SUBJECT])
    review_title = normalize_string(frontmatter[FrontMatterKey.TITLE])
    return f"REVIEW#{review_subject}#TITLE#{review_title}"


def get_review_s3_key(frontmatter: dict) -> str:
    return f"{DocTypeToS3Folder[DocType.REVIEW]}/{normalize_string(frontmatter[FrontMatterKey.TITLE])}"


def get_story_sk(frontmatter: dict) -> str:
    """Returns the sort key for a story."""
    story_title = normalize_string(frontmatter[FrontMatterKey.STORYTITLE])
    return f"TITLE#{story_title}"


def get_story_s3_key(frontmatter: dict) -> str:
    return f"{DocTypeToS3Folder[DocType.STORY]}/{normalize_string(frontmatter[FrontMatterKey.STORYTITLE])}/"


def get_story_chapter_sk(frontmatter: dict) -> str:
    """Returns the sort key for a story."""
    story_title = normalize_string(frontmatter[FrontMatterKey.STORYTITLE])
    chapter_number = frontmatter[FrontMatterKey.CHAPTERNUMBER]
    chapter_number = str(chapter_number).zfill(3)
    return f"TITLE#{story_title}#CHAPTER#{chapter_number}"


def get_story_chapter_s3_key(frontmatter: dict) -> str:
    return f"{DocTypeToS3Folder[DocType.STORYCHAPTER]}/{normalize_string(frontmatter[FrontMatterKey.STORYTITLE])}/{str(frontmatter[FrontMatterKey.CHAPTERNUMBER]).zfill(3)}"


def normalize_string(s: str) -> str:
    """Remove punctuation and replace spaces with hyphens and converts to lowercase."""

    s = s.translate(str.maketrans("", "", string.punctuation))
    return s.replace(" ", "-").lower()
