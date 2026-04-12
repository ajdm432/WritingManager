"""This module handles logic for interfacing with DynamoDB and S3."""
import os
import datetime
from dotenv import load_dotenv
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
import constants
from mgmt_utils import get_file_ext

load_dotenv()

PK_FIELD = constants.DBField.PK
SK_FIELD = constants.DBField.SK

DYNAMO_TABLE_NAME = os.getenv('TABLE_NAME')
dynamo_config = Config(
    connect_timeout=constants.DB_TIMEOUT,
    read_timeout=constants.DB_TIMEOUT,
    retries={
        "total_max_attempts": constants.DB_RETRIES + 1 # includes initial request so +1
    }
)
S3_BUCKET_NAME = os.getenv('BUCKET_NAME')
AWS_REGION = os.getenv('AWS_REGION')

class DBManager():
    """This class handles logic for interfacing with DynamoDB and S3."""
    def __init__(self, metadata, src_path, doc_type):
        self.dynamodb = boto3.resource('dynamodb', config=dynamo_config)
        self.s3 = boto3.resource('s3')
        self.metadata = metadata
        self.src_path = src_path
        self.doc_type = doc_type
        self.doc_pk = constants.get_section_pk(doc_type)
        self.doc_sk = constants.DocTypeToSK[doc_type](metadata)
        self.existing_db_item = None

        if DYNAMO_TABLE_NAME == '':
            raise ValueError('TABLE_NAME environment variable not set.')
        if S3_BUCKET_NAME == '':
            raise ValueError('S3_BUCKET_NAME environment variable not set.')
        if AWS_REGION == '':
            raise ValueError('AWS_REGION environment variable not set.')

        self.table  = self.dynamodb.Table(DYNAMO_TABLE_NAME)
        self.bucket = self.s3.Bucket(S3_BUCKET_NAME)

    def exists_in_db(self):
        """Returns `True` if the document exists in DynamoDB; `False` otherwise."""
        db_resp = self._get_db_item()
        if "Item" not in db_resp or db_resp is None:
            return False
        self.existing_db_item = db_resp["Item"]
        if constants.DBField.CREATED_AT not in self.existing_db_item:
            raise ValueError('Created at field not found on DynamoDB item.')
        return True

    def write_md_to_db(self, publish: bool = False):
        """Writes the document's metadata to DynamoDB."""
        s3_key = constants.DocTypeToS3Folder[self.doc_type]
        s3_key += "/"+self.doc_sk.replace("#", "_")
        s3_key += get_file_ext(self.src_path)
        self.bucket.upload_file(
            self.src_path,
            s3_key
        )
        # write the corresponding entries to dynamodb
        write_items = self._create_db_items(s3_key, publish)
        self._write_batch(write_items)

    def delete_md_from_db(self):
        """Deletes the document's metadata from DynamoDB."""
        if self.existing_db_item is None:
            raise ValueError('Document not found in DynamoDB when attempting to delete.')
        if constants.DBField.S3_PATH not in self.existing_db_item:
            raise ValueError('S3 path field not found on DynamoDB item when attempting to delete.')
        assert self.doc_pk == self.existing_db_item[PK_FIELD]
        assert self.doc_sk == self.existing_db_item[SK_FIELD]
        # need to clean up tag entries as well
        s3_path = self.existing_db_item[constants.DBField.S3_PATH]
        delete_keys = [(self.doc_pk, self.doc_sk)]
        if constants.DBField.TAGS in self.existing_db_item:
            for tag in self.existing_db_item[constants.DBField.TAGS]:
                tag_pk = constants.get_tag_pk(tag)
                delete_keys.append((tag_pk, self.doc_sk))
        for pk, sk in delete_keys:
            self._delete_item(pk, sk)
        # remove item from s3
        self.s3.Object(S3_BUCKET_NAME, s3_path).delete()

    def get_md_status(self) -> bool:
        """Returns the status of the document in DynamoDB."""
        response = self._get_db_item()
        if "Item" not in response:
            raise ValueError('Document not found in DynamoDB when attempting to get status.')
        item = response["Item"]
        if constants.DBField.PUBLISHED not in item:
            raise ValueError('Publication status field not found on DynamoDB item.')
        return item[constants.DBField.PUBLISHED]

    def change_md_status(self):
        """Changes the status of the document in DynamoDB."""
        if constants.DBField.PUBLISHED not in self.existing_db_item:
            raise ValueError('Publication status field not found on DynamoDB item.')
        self.existing_db_item[constants.DBField.PUBLISHED] = not self.existing_db_item[constants.DBField.PUBLISHED]
        self._write_batch([self.existing_db_item])

    def _get_db_item(self):
        """Returns the DynamoDB item for the document."""
        response = None
        try:
            response = self.table.get_item(
                Key={
                    PK_FIELD: self.doc_pk,
                    SK_FIELD: self.doc_sk
                }
            )
        except ClientError as err:
            print("DynamoDB error: %s\nwith code: %s",
                  err.response["Error"]["Message"],
                  err.response["Error"]["Code"]
                )
            raise
        else:
            return response

    def _write_batch(self, items):
        """
        Fills an Amazon DynamoDB table with the specified data.

        :param items: The data to put in the table.
        """
        try:
            with self.table.batch_writer() as writer:
                for i in items:
                    writer.put_item(Item=i)
        except ClientError as err:
            print("Couldn't load data into table %s. Error code: %s. Error message: %s",
                  self.table.name,
                  err.response['Error']['Code'],
                  err.response['Error']['Message']
                )
            raise

    def _delete_item(self, pk, sk):
        """
        Deletes an item from the table.
        """
        try:
            self.table.delete_item(Key={PK_FIELD: pk, SK_FIELD: sk})
        except ClientError as err:
            print(
                "Couldn't delete item %s %s. Here's why: %s: %s",
                pk,
                sk,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

    def _create_db_items(self, s3_path: str, publish: bool = False):
        db_items = []
        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        created_date = now
        updating = False
        created_date = None
        existing_tags = []
        if self.existing_db_item is not None:
            updating = True
            if constants.DBField.CREATED_AT not in self.existing_db_item:
                raise ValueError('Created at field not found on DynamoDB item.')
            created_date = self.existing_db_item[constants.DBField.CREATED_AT]
            if constants.DBField.TAGS in self.existing_db_item:
                existing_tags = self.existing_db_item[constants.DBField.TAGS]

        json = {
            PK_FIELD: self.doc_pk,
            SK_FIELD: self.doc_sk,
            constants.DBField.S3_PATH: s3_path,
            constants.DBField.PUBLISHED: publish,
            constants.DBField.CREATED_AT: created_date,
            constants.DBField.UPDATED_AT: now,
        }

        # required keys used in SK are normalized
        # Preserve original values in dedicated entry fields.
        required_keys = constants.FrontMatterKeySets[self.doc_type]
        for k in required_keys:
            json[k] = self.metadata[k]

        optional_keys = constants.FrontMatterOptional
        found_keys = []
        for k in self.metadata.keys():
            v = self.metadata[k]
            if k in optional_keys:
                json[k] = v
                found_keys.append(k)

        db_items.append(json)

        if constants.DBField.TAGS in found_keys:
            new_tags = self.metadata[constants.DBField.TAGS]
            if updating:
                # need to check if existing tag entries need to be deleted
                for tag in existing_tags:
                    if tag not in new_tags:
                        self._delete_item(constants.get_tag_pk(tag), self.doc_sk)
            for tag in new_tags:
                if tag in existing_tags:
                    # do nothing if this tag already exists
                    continue
                tag_json = {
                    PK_FIELD: constants.get_tag_pk(tag),
                    SK_FIELD: self.doc_sk,
                }
                db_items.append(tag_json)
        return db_items
