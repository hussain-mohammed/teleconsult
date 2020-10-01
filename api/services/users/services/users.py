from datetime import datetime, timedelta

from botocore.exceptions import ClientError
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

from conditions import UserRole, doctor_cond, patient_cond
from constants import LocalConstants
from db_helper import DBHelper
from utils.auth import (
    add_user_to_group,
    get_cognito_user_profile,
    get_current_user_id,
)
from utils.constants import (
    Constants,
    CustomAttrs,
    EnvironVariables,
    Groups,
    Roles,
    StndAttrs,
    Tables,
)
from utils.helper_utils import get_standard_attrs, remove_unwanted_attrs
from utils.logger import logger
from utils.response import ResponseMessage
from schema.users import create_user_schema, doctor_update_schema, patient_update_schema
from utils import find_attribute, get_month_date_range


class UserService:
    def __init__(
        self,
        user_table=None,
        cognito_client=None,
        apts_table=None,
        user_pool_id=EnvironVariables.USER_POOL_ID,
    ):
        self.user_table = user_table
        self.apts_table = apts_table
        self.user_db_instance = DBHelper(self.user_table)
        self.user_pool_id = user_pool_id
        self.cognito_client = cognito_client
        self.apts_db_instance = DBHelper(self.apts_table)

    def get_user(self, user_id):
        """get the user response from dynamodb and cognito.

        Args:
            user_id (str): user id of the user with prefix
        """
        # get the user id of user who currently logged in
        current_user = get_current_user_id()
        user_id = f"{LocalConstants.USER_PREFIX}{user_id}"

        if current_user == user_id:
            # get users' standard attributes from cognito userpool
            user_from_cognito = self.cognito_client.admin_get_user(
                UserPoolId=self.user_pool_id,
                Username=user_id.split(Constants.DYNAMO_KEY_SEPERATOR)[1],
            )
            user_stnd_attrs = get_standard_attrs(user_from_cognito)

            # get users' all the custom attributes from dynamodb
            key = {Constants.PK: user_id, Constants.SK: LocalConstants.USER_PROFILE_SK}
            user_from_dynamo = self.user_db_instance.get_item(key)
            user_dynamo_attrs = user_from_dynamo.get(Constants.ITEM)

            # remove all those user attributes from user details which are not needed in response
            filtered_user_detail = remove_unwanted_attrs(
                {**user_dynamo_attrs, **user_stnd_attrs}
            )
            response = {
                "data": filtered_user_detail,
                "status": True,
                "message": user_from_dynamo.get("message"),
            }
        else:
            response = {
                "status": False,
                "message": LocalConstants.INVALID_USER,
            }
        return response

    def update_user_profile(self, user_id, user_details):
        """this method will update the given updatable fields for a user

        Args:
            user_id (str): user_id of a user with "user#" as prefix.
            user_details (dict): a payload contain the details of a users.

        Returns:
            dict: response with success message.
        """
        user_id = f"{LocalConstants.USER_PREFIX}{user_id}"
        key = {Constants.PK: user_id, Constants.SK: LocalConstants.USER_PROFILE_SK}
        user_resp = self.user_db_instance.get_item(key)
        user = user_resp.get(Constants.ITEM)

        if not user:
            return {"status": False, "message": user_resp.get("message")}

        if user.get(CustomAttrs.ROLE) == Roles.DOCTOR:
            details_tobe_updated = doctor_update_schema.load(user_details, partial=True)

        elif user.get(CustomAttrs.ROLE) == Roles.PATIENT:
            details_tobe_updated = patient_update_schema.load(user_details, partial=True)

        else:
            raise NotImplementedError(
                f"Updating {user.role}'s profile is not implemented yet!"
            )

        key = {Constants.PK: user_id, Constants.SK: LocalConstants.USER_PROFILE_SK}
        updated_user_details = self.user_db_instance.update_item(
            key, details_tobe_updated, details_tobe_updated.keys()
        )
        logger.debug(f"updated_user_details:  {updated_user_details}")
        return updated_user_details

    def create_user(self, user_details):
        """
        This method will take payload and call the boto3 method to create a user inside cognito.

        Args:
            payload (dict): contains user attributes and other user related values.

        Returns:
            dict: response of whether the user created or not.
        """
        create_user_schema.context = {CustomAttrs.ROLE: Roles.PATIENT}
        cognito_attrs = create_user_schema.load(user_details)
        logger.debug(f"cognito_attrs:  {cognito_attrs}")
        create_user_params = {
            "UserPoolId": self.user_pool_id,
            "Username": cognito_attrs.get(StndAttrs.EMAIL),
            "UserAttributes": cognito_attrs.get("user_attrs"),
            "DesiredDeliveryMediums": ["EMAIL"],
        }
        logger.info(create_user_params)

        # If user wants to resend invitation email
        if cognito_attrs.get("message_action"):
            create_user_params["MessageAction"] = "RESEND"
            create_user_params.pop("UserAttributes", None)
        try:
            user_created = self.cognito_client.admin_create_user(**create_user_params)
        except ClientError as client_err:
            logger.exception(client_err)
            raise Exception

        # add user to it's group
        username = user_created["User"]["Username"]
        grp_resp = add_user_to_group(
            self.cognito_client, self.user_pool_id, username, Groups.PATIENT
        )
        logger.debug(f"user added to group: {grp_resp}")

        user_created.pop("ResponseMetadata", None)
        response = {
            "status": True,
            "data": user_created,
            "message": ResponseMessage.USER_ADDED_SUCCESS.format(LocalConstants.USER),
        }
        logger.info(ResponseMessage.USER_ADDED_SUCCESS.format(LocalConstants.USER))
        return response

    def get_appointments_range(self, user_id, start_date, same_month):
        # start_date_obj = datetime.strptime(start_date, LocalConstants.DATETIME_FORMAT)
        start_date_obj = parse(start_date)
        end_date_obj = start_date_obj + relativedelta(day=1, months=+1, days=-1)
        if not same_month:
            end_date_obj = start_date_obj + relativedelta(day=1, months=+2, days=-1)
            start_date_obj += timedelta(1)
        end_date = end_date_obj.isoformat()
        end_date = end_date.replace(end_date.split("T")[1], LocalConstants.MIDNIGHT)

        appointments = self.apts_db_instance.get_range_of_apts(
            Tables.APTS_DOCTOR, user_id, start_date, end_date
        )
        return appointments, start_date_obj, end_date_obj

    def search_user(self, user_payload):
        """search user with the given phone number

        Args:
            user_payload (dict): a dictionary contains user's phone number

        Returns:
            dict: dictionary contains user details, status and success messages.
        """
        phone_number = user_payload.get(StndAttrs.PHONE_NUMBER)
        response = self.cognito_client.list_users(
            UserPoolId=self.user_pool_id,
            AttributesToGet=[StndAttrs.EMAIL],
            Filter=f'{StndAttrs.PHONE_NUMBER}="{phone_number}"',
        )
        users = response.get("Users")

        # no user associated with the given phone number
        if not users:
            return {"status": False, "message": LocalConstants.USER_NOT_EXIST}

        # Assuming that only one user per phone number
        user_id = users[0].get("Username")

        # get user profile from dynamodb to verify user role
        user_profile = get_cognito_user_profile(
            user_id, self.cognito_client, self.user_pool_id
        )

        if user_profile.get(CustomAttrs.ROLE) != Roles.PATIENT:
            response = {"status": False, "message": LocalConstants.INVALID_ROLE}
        else:
            response = {
                "data": {
                    "name": user_profile.get("name"),
                    "email": user_profile.get("email"),
                    "phone_number": phone_number,
                    "user_id": user_id,
                },
                "status": True,
                "message": ResponseMessage.ENTITY_FETCHED.format("User"),
            }
        return response

    def max_slots_per_day(self, user_id, start_date_obj):
        key = {Constants.PK: user_id, Constants.SK: LocalConstants.USER_PROFILE_SK}
        doctor = self.user_db_instance.get_item(key).get(Constants.ITEM)

        operational_slot = doctor.get(LocalConstants.OPERATIONAL_HOURS)  # hh:mm:ss
        operational_days = doctor.get(LocalConstants.OPERATIONAL_DAYS)
        consultation_slot = int(doctor.get(LocalConstants.CONSULTATION_SLOT))
        from_time = datetime.strptime(operational_slot[0], LocalConstants.TIME_FORMAT)
        to_time = datetime.strptime(operational_slot[1], LocalConstants.TIME_FORMAT)

        # diff will be in seconds. It is being converted in mins.
        offset = to_time - from_time
        time_diff = offset.seconds / 60
        max_slots = int(time_diff / consultation_slot)

        end_slot_time = start_date_obj + timedelta(minutes=time_diff)

        return (
            max_slots,
            [from_time, to_time],
            consultation_slot,
            operational_days,
            start_date_obj,
            end_slot_time,
        )

    def group_by_date(self, apts):
        grouped_apts = dict()
        for apt in apts:
            for k, v in apt.items():
                if k == "start_time":
                    date = v.split("T")[0]  # 2020-08-21T00:35:10.473881
                    if date in grouped_apts.keys():
                        grouped_apts[date].append(apt)
                    else:
                        grouped_apts[date] = [apt]
        return grouped_apts

    def check_unavailable_dates(self, grouped_apts, max_slots):
        unavailable_dates = []
        for k, v in grouped_apts.items():
            if len(v) == max_slots:
                unavailable_dates.append(k)
        return set(unavailable_dates)

    def populate_dates(self, start_date, end_date, populated_dts):
        """ It is used to populate days between the given start and end date. eg: 1-5-2000 to 3-5-2000 then 1-5-2000, 2-5-2000, 3-5-2000"""
        curr_time = datetime.utcnow()
        for day in range(int((end_date - start_date).days) + 1):
            populated_dts.append(
                (start_date + timedelta(day)).replace(
                    hour=curr_time.hour, minute=curr_time.minute
                )
            )
        return set(populated_dts)

    def filter_based_on_weekdays(self, avail_dates, doc_op_days):
        filtered_dates = []
        for date in avail_dates:
            week_day = date.weekday()
            day_name = LocalConstants.day_name[week_day]
            if day_name in doc_op_days:
                filtered_dates.append(date)
        return filtered_dates

    def get_available_dates(self, user_id, start_date):
        start_date_obj = parse(start_date)
        user_id = f"{LocalConstants.USER_PREFIX}{user_id}"
        populated_dts = []
        current_date = datetime.utcnow()  # 2020-08-21T00:35:10.473881
        (
            max_slots,
            doc_hours,
            doc_slot_dur,
            doc_operational_days,
            slot_start_time,
            end_slot_time,
        ) = self.max_slots_per_day(user_id, start_date_obj)
        # start_date_obj = datetime.strptime(start_date, LocalConstants.DATETIME_FORMAT)

        # Check if the user wants to check the availability for current date as well
        if start_date_obj.date() == current_date.date():
            month_last_date = slot_start_time + relativedelta(day=1, months=+1, days=-1)
            if slot_start_time.day != month_last_date.day:
                tomorrow = slot_start_time + timedelta(1)
                start_date = tomorrow.isoformat()
            # start_date = tomorrow.replace(
            #     tomorrow.split("T")[1], LocalConstants.NEWDAY
            # )  # just increment by one day and follow the same pattern
            if slot_start_time <= current_date <= end_slot_time:
                # checking if the current time lies between doctors operational hours
                # calculating remaining slots left for the current day
                rem_time_in_mins = ((end_slot_time - current_date).seconds) / 60
                rem_slots = int(rem_time_in_mins / doc_slot_dur)

                if rem_slots > 0:
                    end_date = end_slot_time
                    appointments = self.apts_db_instance.get_range_of_apts(
                        Tables.APTS_DOCTOR,
                        user_id,
                        current_date.isoformat(),
                        end_date.isoformat(),
                    )
                    if len(appointments) < rem_slots:
                        populated_dts.append(current_date)
        else:
            start_date = slot_start_time.isoformat()

        if start_date:
            same_month = True
            if parse(start_date).month != start_date_obj.month:
                same_month = False

            appointments, start_date_obj, end_date_obj = self.get_appointments_range(
                user_id, start_date, same_month
            )
            populated_dates = self.populate_dates(
                start_date_obj, end_date_obj, populated_dts
            )
        grouped_apts = self.group_by_date(appointments)
        unavailable_dates = self.check_unavailable_dates(grouped_apts, max_slots)
        all_available_dates = populated_dates - unavailable_dates
        available_dates = self.filter_based_on_weekdays(
            list(all_available_dates), doc_operational_days
        )
        response = {
            "data": {"available_dates": [d.isoformat() for d in available_dates]},
            "status": True,
            "message": ResponseMessage.ENTITY_FETCHED.format(
                LocalConstants.AVAILABLE_DATES
            ),
        }
        return response

    def get_available_slots(self, user_id, apt_date):
        """calculated all the available slots of a doctor on the given date

        Args:
            user_id (str): user id of the doctor.
            apt_date (str): date of on which slot has to be booked.

        Returns:
            dict: dictionary with response.
        """
        apt_date_obj = parse(apt_date)
        user_id = f"{LocalConstants.USER_PREFIX}{user_id}"
        (
            max_slots,
            consult_slot,
            consult_slot_dur,
            doc_operational_days,
            consult_starts_at,
            consult_ends_at,
        ) = self.max_slots_per_day(user_id, apt_date_obj)

        # calculating total slots of a doctor
        total_slots = self.get_total_slots(
            consult_starts_at, max_slots, consult_slot_dur
        )

        today = datetime.utcnow().replace(
            day=consult_starts_at.day,
            month=consult_starts_at.month,
            year=consult_starts_at.year,
        )
        today_date = today.date()

        # appointment has to be booked today
        if consult_starts_at.date() == today_date:
            total_slots = self.get_updated_total_slots(total_slots)

        # appointment has to be booked in past days. NOT POSSIBLE
        elif consult_starts_at.date() < today_date:
            return {"status": False, "message": LocalConstants.INVALID_DATE}

        if total_slots:

            # calculating total booked slots of a doctor
            booked_slots = self.get_list_of_booked_slots(
                user_id, consult_starts_at, parse(total_slots[-1])
            )
            remaining_slots = set(total_slots) - set(booked_slots)
        else:
            remaining_slots = []

        return {
            "data": sorted(remaining_slots),
            "status": True,
            "message": ResponseMessage.ENTITY_FETCHED.format("Slots"),
        }

    def get_total_slots(self, consult_starts_at, max_slots, consult_slot_dur):
        """retrieve the total possible slots for a given doctor

        Args:
            consult_starts_at (str): time when doctor start his/her consultations.
            max_slots (str): total number of slots a doctor can have.
            consult_slot_dur (int): duration of each slot.

        Returns:
            object: a map object contain all slots.
        """
        slots_on_given_date = [consult_starts_at]
        for slot_no in range(max_slots - 1):
            next_apt_at = slots_on_given_date[slot_no] + timedelta(
                minutes=consult_slot_dur
            )
            slots_on_given_date.append(next_apt_at)

        iso_slots_on_given_date = list(
            map(lambda date: date.isoformat(), slots_on_given_date)
        )

        return iso_slots_on_given_date

    def get_updated_total_slots(self, total_slots):
        """generate a new appointment start time for a doctor

        Args:
            total_slots (object): doctor's list of all slots for the day.
            current_time (int): current time date object.

        Returns:
            object: date time object
        """
        current_time = datetime.utcnow()
        for index, slot in enumerate(total_slots):
            if parse(slot) > current_time:
                return total_slots[index:]
        return []

    def get_list_of_booked_slots(self, user_id, consult_starts_at, consult_ends_at):
        """retrieve the list of all booked slots of a doctor

        Args:
            user_id (str): user id of a doctor.
            consult_starts_at (object): doctor consultation time starts at
            consult_ends_at (object): doctor consultation time ends at

        Returns:
            list: list of all booked slots
        """
        doctor_schedule = self.apts_db_instance.get_range_of_apts(
            Tables.APTS_DOCTOR,
            user_id,
            consult_starts_at.isoformat(),
            consult_ends_at.isoformat(),
        )
        booked_slots = []
        for booked_slot in doctor_schedule:
            booked_slots.append(booked_slot.get("start_time"))

        return booked_slots

    def get_user_appointmens(self, user_id, date):
        _user_id = f"{LocalConstants.USER_PREFIX}{user_id}"

        # get the user id of user who currently logged in
        current_user = get_current_user_id()
        if _user_id == current_user:
            user = self.cognito_client.admin_get_user(
                UserPoolId=self.user_pool_id, Username=user_id,
            )
            role = find_attribute(user.get("UserAttributes"), LocalConstants.CUSTOM_ROLE)
            start, end = get_month_date_range(date)

            # initiating userRole class to get the role based index name and column name
            user_role = UserRole(role)
            db_entities = patient_cond(user_role) or doctor_cond(user_role)

            if db_entities:
                response = self.apts_db_instance.get_appointment_between_dates(
                    db_entities.get("index"),
                    db_entities.get("col"),
                    _user_id,
                    [start, end],
                )
                return {
                    "data": response,
                    "status": True,
                    "message": ResponseMessage.ENTITY_FETCHED.format(LocalConstants.APT),
                }
        return {"status": False, "message": LocalConstants.INVALID_USER}
