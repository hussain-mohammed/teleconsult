import os

import pytest
from moto import mock_cognitoidp, mock_dynamodb2

from utils.aws_clients import AWSConnections
from utils.constants import AwsResources

TableName = "practices"


@pytest.fixture(scope="module")
def aws_credentials():
    # Mocked AWS credentials for moto
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


def pytest_configure():
    return {"pid": None, "pk": None}


@pytest.yield_fixture(scope="module")
def dynamodb_client(aws_credentials):
    # DDB mock client
    with mock_dynamodb2():
        conn = AWSConnections(AwsResources.DYNAMODB).get_client()
        yield conn


@pytest.yield_fixture(scope="module")
def dynamodb_resource(aws_credentials):
    # DDB mock resource
    with mock_dynamodb2():
        conn = AWSConnections(AwsResources.DYNAMODB).get_resource()
        yield conn


@pytest.yield_fixture(scope="module")
def cognito_client(aws_credentials):
    with mock_cognitoidp():
        conn = AWSConnections(AwsResources.COGNITOIDP).get_client()
        yield conn
