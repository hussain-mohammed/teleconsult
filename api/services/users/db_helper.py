from boto3.dynamodb.conditions import Attr, Key

from constants import AptStatus, LocalConstants
from utils.constants import AppAttrs, Constants
from utils.db_utilities import DBUtilities
from utils.logger import logger
from utils.response import ResponseMessage


class DBHelper(DBUtilities):
    def __init__(self, table_obj):
        super().__init__(table_obj)

    def get_range_of_apts(self, indexname, user_id, start_date, end_date):
        response = self.table_obj.query(
            IndexName=indexname,
            KeyConditionExpression=Key(LocalConstants.DOCTOR_ID).eq(user_id)
            & Key(LocalConstants.START_TIME).between(start_date, end_date),
            FilterExpression=Attr(LocalConstants.STATUS).ne(AptStatus.RESCHEDULED)
            & Attr(LocalConstants.STATUS).ne(AptStatus.PATIENT_CANCEL)
            & Attr(LocalConstants.STATUS).ne(AptStatus.PATIENT_CANCEL_REQUEST),
        )
        apts = response.get(Constants.ITEMS)
        logger.info(ResponseMessage.ENTITY_FETCHED.format(AppAttrs.RECORD))
        return apts

    def get_appointment_between_dates(self, index_name, col, user_id, apt_time):
        """get list of all the appointments b/w given dates

        Args:
            index_name (GSI): name of index (gsi).
            user_id (str): user id of a patient/doctor.
            apt_time (list): contain start and end time of appointment.

        Returns:
            boolean: true if user is not available
        """
        response = self.table_obj.query(
            IndexName=index_name,
            KeyConditionExpression=Key(col).eq(user_id)
            & Key(LocalConstants.START_TIME).between(apt_time[0], apt_time[1]),
        )
        items = response.get(Constants.ITEMS)
        items = items if items else []
        return items
