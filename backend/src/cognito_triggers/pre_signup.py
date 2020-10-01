from utils.aws_clients import AWSConnections
from utils.constants import AwsResources, Constants, Roles, Tables
from utils.db_utilities import DBUtilities
from utils.logger import logger

logger.debug(Tables.USERS_TABLE)
user_table = (
    AWSConnections(AwsResources.DYNAMODB).get_resource().Table(Tables.USERS_TABLE)
)
db_instance = DBUtilities(user_table)


def handler(event, context):
    """Handler for cognito pre-signup lambda trigger to store the
        custom attributes in dynamodb

    Args:
        event (object): Cognito event
        context (object): Cognito context

    Returns:
        object: Cognito event
    """
    custom_attributes = {}

    # making sure there should not be another user registered with the given phone number
    user_phone_no = event.get("request").get("userAttributes").get("phone_number")
    logger.debug(f"user_phone_no:  {user_phone_no}")
    if is_user_exist(user_phone_no):
        raise ValueError("A user already exists with given phone number")

    # Extracting the custom attributes from the cognito event.
    for k, v in event["request"]["userAttributes"].items():
        if k.startswith("custom:"):
            k = k.split(":")[1]
            custom_attributes[k] = v

    custom_attributes["pk"] = f"user#{event['userName']}"
    custom_attributes["sk"] = "profile"
    custom_attributes["is_deleted"] = "false"

    # Add cvo verified field if the user is a doctor
    if custom_attributes["role"] == Roles.DOCTOR:
        custom_attributes[Constants.IS_CVO_VERIFIED] = False

    # adding custom attributes to dynamodb
    db_resp = db_instance.insert_item(custom_attributes)
    logger.debug(db_resp)
    return event
