from flask import Flask, request

from constants import LocalConstants, LocalUriPaths
from utils.aws_clients import AWSConnections
from utils.constants import AwsResources, HttpVerbs, Tables
from utils.logger import logger
from utils.response import CustomResponse, Status
from services.users import UserService

app = Flask(__name__)

cognito_client = AWSConnections(AwsResources.COGNITOIDP).get_client()
user_table = (
    AWSConnections(AwsResources.DYNAMODB).get_resource().Table(Tables.USERS_TABLE)
)

user_services = UserService(
    user_table=user_table, cognito_client=cognito_client,
)


@app.route(LocalUriPaths.GET_USER, methods=[HttpVerbs.GET])
def get_user(user_id):
    response = CustomResponse()
    user_resp = user_services.get_user(user_id)
    response.set_entities(user_resp)
    logger.debug(user_resp)
    return response.get_response()


@app.route(LocalUriPaths.UPDATE_USER_PROFILE, methods=[HttpVerbs.PUT])
def update_user_profile(user_id):
    response = CustomResponse()
    user_details = request.get_json()
    logger.debug(user_details)
    updated_details = user_services.update_user_profile(user_id, user_details)
    if not updated_details.get("status"):
        response.status = Status.HTTP_400_BAD_REQUEST
    response.set_entities(updated_details)
    return response.get_response()


@app.route(LocalUriPaths.CREATE_USER, methods=[HttpVerbs.POST])
def create_user():
    response = CustomResponse()
    user_details = request.get_json()
    user_created = user_services.create_user(user_details)
    logger.debug(user_created)
    response.set_entities(user_created)
    return response.get_response()


@app.route(LocalUriPaths.SEARCH_USER, methods=[HttpVerbs.POST])
def search_user():
    response = CustomResponse()
    user_payload = request.get_json()
    user_found = user_services.search_user(user_payload)
    if not user_found.get("status"):
        response.status = Status.HTTP_400_BAD_REQUEST
    logger.debug(user_found)
    response.set_entities(user_found)
    return response.get_response()


@app.route(LocalUriPaths.GET_DOCTOR_DATES, methods=[HttpVerbs.GET])
def get_doctors_available_dates(user_id):
    response = CustomResponse()
    start_date = request.args.get(LocalConstants.START_DATE)
    available_dates = user_services.get_available_dates(user_id, start_date)
    response.set_entities(available_dates)
    logger.debug(available_dates)
    return response.get_response()


@app.route(LocalUriPaths.GET_AVAILABLE_SLOTS, methods=[HttpVerbs.GET])
def get_doctors_available_slots(user_id):
    response = CustomResponse()
    apt_date = request.args.get(LocalConstants.DATE)
    available_slots = user_services.get_available_slots(user_id, apt_date)
    if not available_slots.get("status"):
        response.status = Status.HTTP_400_BAD_REQUEST
    logger.debug(available_slots)
    response.set_entities(available_slots)
    return response.get_response()


@app.route(LocalUriPaths.GET_USER_APTS, methods=[HttpVerbs.GET])
@app.route(LocalUriPaths.TEMP_USER_APTS, methods=[HttpVerbs.GET])
def get_user_appointments(user_id, date=None):
    response = CustomResponse()
    if not date:
        date = request.args.get(LocalConstants.DATE)
    apts = user_services.get_user_appointmens(user_id, date)
    if not apts.get("status"):
        response.status = Status.HTTP_400_BAD_REQUEST
    logger.debug(apts)
    response.set_entities(apts)
    return response.get_response()
