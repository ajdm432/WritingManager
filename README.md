# WritingManager

A CLI tool for managing a personal database of writing projects. WritingManager validates local Markdown files with structured YAML frontmatter and stores them in AWS (DynamoDB for metadata, S3 for file content).

## Supported Document Types

WritingManager currently supports three document types: **articles**, **reviews**, and **story chapters**. Adventure and story types are planned but not yet implemented.
Here's a quick breakdown of what these mean:
| Document Type | Description |
| -------- | ------- |
| article | An article about some topic |
| review | A review about some product or piece of media |
| story | A folder that defines a story, as well as presentation elements for front-end display (background images, cover, logo, styling) |
| story chapter | A chapter that belongs to a story |
| adventure module | A folder containing data for an adventure module for a TTRPG system. Can contain any documents, but usually stores pdfs |

## Requirements

- Python 3.10+
- An AWS account with a configured DynamoDB table and S3 bucket (see [AWS Setup](#aws-setup))
- User has [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html) installed
- User has configured credentials for an AWS IAM user with full permissions for DynamoDB and S3 using the `aws configure` CLI command

## Installation

```bash
git clone <repo-url>
cd WritingManager
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

```
TABLE_NAME = YourDynamoDBTableName
BUCKET_NAME = YourS3BucketName
```

## Markdown File Format

Each Markdown file must include YAML frontmatter with a `type` field and the required fields for that type.

### Article

```yaml
---
type: article
category: Technology
title: My Article Title
---
```

### Review

```yaml
---
type: review
subject: Film
title: My Review Title
---
```

### Story Chapter

```yaml
---
type: story_chapter
story_title: My Story
chapter_number: 1
chapter_title: The Beginning
---
```

### Optional Fields

All document types may also include:

- `author` - Author name
- `tags` - A list of tags (e.g. `[fantasy, adventure]`)

## Usage

Run the tool and provide a path to a Markdown file when prompted:

```bash
python main.py
```

```
Please provide a path to the file or folder you would like to add to your site:
> path/to/my-article.md
```

The tool will parse the file's frontmatter, display the detected document type and metadata, and ask you to confirm. From there:

- **New document** - You'll be asked whether to add it to the database.
- **Existing document** - You'll be given three options:
  1. **Replace** the existing entry with the new file.
  2. **Delete** the existing entry from the database and S3.
  3. **Change publication status** (toggle between published and unpublished).

## AWS Setup

WritingManager expects the following AWS resources to exist:

### DynamoDB Table

A single table with a composite primary key:

| Key           | Field Name | Type   |
| ------------- | ---------- | ------ |
| Partition Key | `header`   | String |
| Sort Key      | `id`       | String |

The tool writes items using key patterns like:

- **Partition key**: `SECTION#article`, `SECTION#review`, `TAG#my-tag`, etc.
- **Sort key**: Generated from document metadata, e.g. `CATEGORY#technology#TITLE#my-article-title`

If you wish to change expected field names or frontmatter fields, please edit `constants.py`.

### S3 Bucket

A standard S3 bucket. The tool uploads files into subfolders by document type:

- `articles/`
- `reviews/`
- `story_chapters/`

### IAM Permissions

The configured AWS credentials need the following permissions on the respective resources:

- **DynamoDB**: `GetItem`, `BatchWriteItem`, `DeleteItem`
- **S3**: `PutObject`, `DeleteObject`

## License

MIT
