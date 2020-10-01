from contextlib import contextmanager

import pytest
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

# from docs.db_utilities import insert_items, get_items

BUCKET = "some-bucket"
KEY = "incoming/transaction-0001.txt"
BODY = "Hello World!"

event = {"key": KEY, "bucket": BUCKET, "body": BODY}


@contextmanager
def s3_setup(s3_resource):

    s3_resource.create_bucket(Bucket=event["bucket"])
    yield


class TestClassS3:
    def test_create_bucket(self, s3_resource):
        with s3_setup(s3_resource):
            response = s3_resource.buckets.all()
            for bucket in response:
                if bucket == event["bucket"]:
                    assert bucket == event["bucket"]
                else:
                    assert bucket != event["bucket"]

    def test_put_object(self, s3_resource):
        s3_resource.Object(event["bucket"], event["key"]).put(Body=event["body"])
        object_response = s3_resource.Object(event["bucket"], event["key"]).get()
        assert object_response["Body"].read().decode() == event["body"]
