from contextlib import contextmanager

from botocore.exceptions import ClientError

from utils.logger import logger


@contextmanager
def create_user_pool(cognito_client):
    """
    creating dummy user_pool

    Args:
        cognito_client (moto_client_object): moto connection to access the mocked environment

    Returns:
        string: error string if moto is throwing some error

    Yields:
        string: user_pool_id
    """
    try:
        user_pool_obj = cognito_client.create_user_pool(
            PoolName="testpool",
            Policies={
                "PasswordPolicy": {
                    "RequireUppercase": True,
                    "RequireLowercase": True,
                    "RequireNumbers": True,
                    "RequireSymbols": True,
                }
            },
            AutoVerifiedAttributes=["email"],
            UsernameAttributes=["email"],
        )
        yield user_pool_obj["UserPool"]["Id"]
    except ClientError as client_err:
        logger.debug(client_err.response["error"]["message"])
        return str(client_err)


user_payload = [
    {
        "name": "user",
        "email": "p1@mailinator.com",
        "phone_number": "+919000000000",
        "role": "p",
        "message_action": False,
    },
    {
        "name": "Admin",
        "email": "p2@mailinator.com",
        "phone_number": "+919000000000",
        "role": "p",
        "message_action": False,
    },
    {
        "name": "John",
        "email": "p3@mailinator.com",
        "phone_number": "+919000000000",
        "role": "p",
        "message_action": False,
    },
    {
        "name": "Mock1",
        "email": "p5@mailinator.com",
        "role": "p",
        "message_action": False,
    },
    {"name": "Mock", "email": "p5@mailinator.com", "role": "p", "message_action": True},
]


TableName = "users"


@contextmanager
def ddb_setup(dynamodb_resource):
    # create mock ddb bucket and object to be available to all methods in the test class
    dynamodb_resource.create_table(
        TableName=TableName,
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
            {"AttributeName": "email", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "gsi_email",
                "KeySchema": [{"AttributeName": "email", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "KEYS_ONLY"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 2,
                    "WriteCapacityUnits": 2,
                },
            },
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 2, "WriteCapacityUnits": 2},
    )
    yield
