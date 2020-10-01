from datetime import datetime

from dateutil.parser import parse

from constants import LocalConstants
from db_helper import db_instance, get_apts_list
from utils.constants import Constants
from utils.logger import logger


def handler(event, context):
    """Handler for scheduler cron job. This is used to check unfinished appointments and put them to incomplete status.

    Args:
        event (object): Event Object
        context (object): context
    """
    # We can customize this to write logs to Dynamodb
    ongoing_apts = get_apts_list(LocalConstants.STATUS_GSI, LocalConstants.ONGOING)
    d_req_cancel_apts = get_apts_list(
        LocalConstants.STATUS_GSI, LocalConstants.DOCTOR_CANCEL_REQUEST
    )
    p_req_cancel_apts = get_apts_list(
        LocalConstants.STATUS_GSI, LocalConstants.PATIENT_CANCEL_REQUEST
    )

    for apts in (ongoing_apts, d_req_cancel_apts, p_req_cancel_apts):
        for apt in apts:
            logger.debug(f"appointment- {apt}")
            key = {Constants.PK: apt.get(Constants.PK)}
            end_time = parse(apt.get(LocalConstants.END_TIME))
            current_time = datetime.utcnow()
            if current_time > end_time:
                if apt.get(Constants.STATUS) == LocalConstants.ONGOING:
                    # Updating Ongoing status
                    update_status = {
                        Constants.STATUS: LocalConstants.INCOMPLETED,
                        LocalConstants.CALL_STATUS: LocalConstants.INCOMPLETED,
                    }
                else:
                    # Updating cancellation requested status
                    update_status = {
                        Constants.STATUS: LocalConstants.CANCELLED,
                        LocalConstants.CALL_STATUS: LocalConstants.CANCELLED,
                    }
                db_instance.update_item(key, update_status, update_status.keys())
    logger.debug(LocalConstants.SCHEDULER_COMPLETED_MSG)
