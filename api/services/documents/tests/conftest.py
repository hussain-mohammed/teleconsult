import os

import boto3
import pytest
from moto import mock_dynamodb2, mock_s3


@pytest.fixture(scope="module")
def aws_credentials():
    # Mocked AWS credentials for moto
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.yield_fixture(scope="module")
def dynamo_client(aws_credentials):
    # DDB mock client
    with mock_dynamodb2():
        conn = boto3.client("dynamodb", region_name="ap-south-1")
        yield conn


@pytest.yield_fixture(scope="module")
def dynamo_resource(aws_credentials):
    # DDB mock client
    with mock_dynamodb2():
        conn = boto3.resource("dynamodb", region_name="ap-south-1")
        yield conn


@pytest.yield_fixture(scope="module")
def s3_resource(aws_credentials):
    # DDB mock client
    with mock_s3():
        conn = boto3.resource("s3")
        yield conn


@pytest.yield_fixture(scope="module")
def s3_client(aws_credentials):
    # DDB mock client
    with mock_s3():
        conn = boto3.client("s3")
        yield conn
