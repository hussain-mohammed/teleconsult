from utils.aws_clients import AWSConnections
from utils.constants import AwsResources, Constants, Tables
from utils.db_utilities import DBUtilities
from utils.logger import logger

user_table = (
    AWSConnections(AwsResources.DYNAMODB).get_resource().Table(Tables.USERS_TABLE)
)
db_instance = DBUtilities(user_table)
s3_client = AWSConnections(AwsResources.S3).get_client()


def handler(event, context):
    """Handler for S3 object created trigger

    Args:
        event (object): Event Object
        context (object): context
    """
    # We can customize this to write logs to Dynamodb
    logger.debug(event)
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"].replace("+", " ")
    metadata = s3_client.head_object(Bucket=bucket, Key=key)
    user_id = metadata["ResponseMetadata"]["HTTPHeaders"]["x-amz-meta-user_id"]
    logger.debug(metadata)
    logger.debug(user_id)
    dynamodb_key = {Constants.PK: f"user#{user_id}", Constants.SK: "profile"}
    payload = {
        "profile_pic": key.split("/")[1]
    }  # storing only the filename, not the whole file structure.
    db_resp = db_instance.update_item(dynamodb_key, payload, payload.keys())
    logger.debug(db_resp)
    return event
