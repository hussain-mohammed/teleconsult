import json

from flask import jsonify, make_response, request

from .constants import Constants
from .logger import logger


class ResponseMessage:
    SERVER_ERROR_MSG = "Internal server error occurred."
    TYPE_ERROR_MSG = (
        "Operation or function is applied to an object of an inappropriate type."
    )
    KEY_ERROR_MSG = "Entity does not exist."
    NO_UPDATE_MSG = "Entity is already up to date."
    ENTITY_ADDED = "{} added successfully."
    ENTITY_FETCHED = "{} fetched successfully."
    ENTITY_UPDATED = "{} updated successfully."
    ENTITY_DELETED = "{} deleted successfully."
    GENERIC_ERROR_MSG = "Unexpected error occurred, contact to server team."
    USER_VERIFICATION_MSG = "User verified successfully."
    USER_ADDED_SUCCESS = "{} created successfully."
    FILE_READ_ERROR = "Error while reading the template file."
    AWS_GENERIC_ERROR = "Something wrong happened while accessing AWS resources."
    MSG_SUCCESS = "{} sent successfully."
    MSG_FAILED = "{} failed."
    CUSTOM_MSG_EMAIL_VERIFY = (
        "Custom message for email verification has been sent to user."
    )
    LOCATION_ERROR_MSG = "Latitude or Longitude is not provided."
    EXIST_ERROR_MSG = "{} already exist."
    ADDRESS_ERROR_MSG = "Door, street or city is not provided."
    USER_ROLE_MSG = "Given role is not valid for the user."


class ExceptionHandlingMessages:
    """
    prepare error specific messages
    """

    class ExceptionTypes:
        BASIC = "basic_error_msgs"
        AWS = "aws_error_msgs"

    def __init__(self):
        self.msgs = self.read_messages()

    def read_messages(self):
        msgs_file_path = Constants.ERROR_MESSAGES_FILE_PATH
        with open(msgs_file_path) as f:
            try:
                error_messages = json.load(f)
            except Exception:
                return {}
        return error_messages

    def get_message(
        self,
        error_obj,
        e_type: str,
        default_message: str = ResponseMessage.GENERIC_ERROR_MSG,
    ):
        if isinstance(error_obj, Exception):
            exception_name = error_obj.__class__.__name__
        else:
            exception_name = error_obj
        msgs_obj = self.msgs.get(e_type)
        error_msg = msgs_obj.get(exception_name, default_message)
        return error_msg


exception_msgs = ExceptionHandlingMessages()


class Status:
    HTTP_200_OK = 200
    HTTP_201_CREATED = 201
    HTTP_204_NO_CONTENT = 204
    HTTP_400_BAD_REQUEST = 400
    HTTP_401_UNAUTHORIZED = 401
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404
    HTTP_409_CONFLICT = 409
    HTTP_500_INTERNAL_SERVER_ERROR = 500


class BadRequestException(Exception):
    def __init__(self, message, errors=None):
        super(BadRequestException, self).__init__(message)
        self.message = message
        self.errors = errors
        self.status = Status.HTTP_400_BAD_REQUEST
        self.data = {"error": message}
        self.headers = {}

    def get_data(self):
        return jsonify(self.data)


class CustomResponse(object):

    CUSTOM_HEADERS = {
        # We assume that we are allowing all Origins
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT",
        "Access-Control-Allow-Headers": "Content-Type",
    }

    def __init__(self):
        self.data = {"results": []}
        self.headers = self.get_custom_headers()
        self.status = Status.HTTP_200_OK
        self.is_success = True

    def get_custom_headers(self):
        try:
            self.CUSTOM_HEADERS[
                "Access-Control-Allow-Methods"
            ] = f"OPTIONS,{request.method}"
            return self.CUSTOM_HEADERS
        except Exception as e:
            logger.exception(str(e))
            return self.CUSTOM_HEADERS

    def set_header(self, key, value):
        self.headers[key] = value

    # output entities
    def set_entities(self, entities):
        self.data["results"] = entities

    def get_response(self):
        return make_response(jsonify(self.data), self.status, self.headers)

    def set_failure(self, error, status=Status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.data["error"] = error
        self.status = status
        self.is_success = False
