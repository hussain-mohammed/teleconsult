from boto3.dynamodb.conditions import Key

from utils.aws_clients import AWSConnections
from utils.constants import AwsResources, Constants, Tables
from utils.db_utilities import DBUtilities

apt_table = (
    AWSConnections(AwsResources.DYNAMODB).get_resource().Table(Tables.APPOINTMENTS)
)
db_instance = DBUtilities(apt_table)

def get_apts_list(indexname, status):
    """
    method to fetch all the apts of a particular status from the database
    :param indexname: GSI name
    :param status: status
    """
    response = apt_table.query(
        IndexName=indexname, KeyConditionExpression=Key(Constants.STATUS).eq(status)
    )
    item = response.get(Constants.ITEMS)
    return item
