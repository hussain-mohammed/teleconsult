import os


def get_full_path(path):
    """
    this will return you full path from the given absolute path
    path: absolute path of the file
    return: path object
    """
    full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path,)
    return full_path


class UriPaths:
    SPECIALITIES = "/public/specialties"
    PRACTICE_ADMIN = "/public/practiceadmins"
    GET_PA = "/public/practiceadmins/<string:username>"


class HttpVerbs:
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class Constants:
    # Global constant values
    IS_OFFLINE = os.environ.get("IS_OFFLINE", "false") == "true"

    STATUS = "status"
    MESSAGE = "message"

    EVENT_RESOURCE = "events"

    # API routes
    API_GATEWAY_HOST = os.environ.get("API_GATEWAY_HOST", "http://localhost/")
    # website's base URL
    WEB_DOMAIN = os.environ.get("WEB_DOMAIN", "http://localhost/")

    # Secret key for signed url for CVO verification
    SECURED_URL_SECRET_KEY = os.environ.get("SECURED_URL_SECRET_KEY")
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT")

    # DB Field constants
    IS_CVO_VERIFIED = "is_cvo_verified"
    METADATA = "metadata"
    IS_DELETED = "is_deleted"
    PK = "pk"
    SK = "sk"
    PID = "practice_id"
    BID = "branch_id"
    UID = "user_id"
    ITEMS = "Items"
    ITEM = "item"
    DYNAMO_KEY_SEPERATOR = "#"

    # Booleans
    FALSE = "false"
    TRUE = "true"

    # JSON File for error ERROR_MESSAGES
    ERROR_MESSAGES_FILENAME = "error_codes.json"
    ERROR_MESSAGES_FILE_PATH = get_full_path(ERROR_MESSAGES_FILENAME)

    USERS_UNUPDATEABLE_FIELDS = [
        "pk",
        "user_type",
        "email",
        "license_number",
        "gender",
        "dob",
    ]


class StndAttrs:
    EMAIL = "email"
    PHONE_NUMBER = "phone_number"
    NAME = "name"
    EMAIL_VERIFIED = "email_verified"
    PHONE_VERIFIED = "phone_number_verified"
    SUB = "sub"


class CustomAttrs:
    ROLE = "role"
    IS_DELETED = "is_deleted"


class Tables:
    TABLE_OBJ = "table_obj"
    APPOINTMENTS = os.environ.get("APPOINTMENTS_TABLE")
    DOCUMENTS_TABLE = os.environ.get("DOCUMENTS_TABLE")
    USERS_TABLE = os.environ.get("USERS_TABLE")
    PRACTICES = os.environ.get("PRACTICES_TABLE")

    GSI_PATIENT_APPOINTMENT = "gsi_patient_appointment"
    GSI_PRACTICES_EMAIL = "gsi_email_exists"
    GSI_USERWISE = "gsi_userwise"
    GSI_BRANCHWISE = "gsi_branchwise"

    # Appointments GSI Names
    APTS_PRACTICE = "apts_practice"
    APTS_BRANCH = "apts_branch"
    APTS_DOCTOR = "apts_doctor"
    APTS_PATIENT = "apts_patient"


class EmailConstants:
    CVO_EMAIL_SUBJECT = "Locqum: Verification of the doctor's credentials."
    EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
    SENDER_NAME = os.environ.get("SENDER_NAME")
    CVO_EMAIL = os.environ.get("CVO_EMAIL")
    CVO_CC_EMAIL = os.environ.get("CVO_CC_EMAIL")
    CHARSET = "UTF-8"
    INVITE_EMAIL_TEMPLATE = get_full_path(
        "templates/email/user_invitation_template.html"
    )
    INVITE_EMAIL_SUBJECT = "Locqum Telemedicine: Invitation to Join Platform"
    VERIFICATION_EMAIL_TEMPLATE = get_full_path(
        "templates/email/verification_template.html"
    )
    VERIFICATION_CODE_EMAIL_SUBJECT = "Locqum Telemedicine: Email Verification"
    FORGOT_PASS_EMAIL_SUBJECT = "Locqum Telemedicine: Forgot Password Verification Code"


class EmailTempName:
    CVO_EMAIL_TEMP = os.environ.get("CVO_EMAIL_TEMP")
    NEW_DOC_TEMP = os.environ.get("NEW_DOC_TEMP")
    INVITE_USER_TEMP = os.environ.get("INVITE_USER_TEMP")
    CONFIRM_APT_DOCTOR = os.environ.get("CONFIRM_APT_DOCTOR")
    CONFIRM_APT_PATIENT = os.environ.get("CONFIRM_APT_PATIENT")
    CANCEL_APT_DOCTOR = os.environ.get("CANCEL_APT_DOCTOR")
    CANCEL_APT_PATIENT = os.environ.get("CANCEL_APT_PATIENT")
    RESCHEDULE_APT_DOCTOR = os.environ.get("RESCHEDULE_APT_DOCTOR")
    RESCHEDULE_APT_PATIENT = os.environ.get("RESCHEDULE_APT_PATIENT")
    DOCTOR_THANKYOU_EMAIL = os.environ.get("DOCTOR_THANKYOU_EMAIL")
    CANCELLATION_APT_REQUEST = os.environ.get("CANCELLATION_APT_REQUEST")


class Groups:
    PATIENT = "Patients"
    DOCTOR = "Doctors"
    PRACTICE_ADMIN = "PracticeAdmin"
    BRANCH_ADMIN = "BranchAdmin"


class Roles:
    PATIENT = "P"
    DOCTOR = "D"
    PRACTICE_ADMIN = "PA"
    BRANCH_ADMIN = "BA"
    ROLE_ATTR_NAME = "custom:role"


class AwsResources:
    DYNAMODB = "dynamodb"
    COGNITOIDP = "cognito-idp"
    COGNITOIDT = "cognito-identity"
    S3 = "s3"
    SES = "ses"


class EnvironVariables:
    USER_POOL_ID = os.environ.get("USER_POOL_ID")
    LOCAL_URLS = {
        AwsResources.DYNAMODB: os.environ.get(
            "DYNAMODB_LOCAL_URL", "http://localhost:8000"
        ),
        AwsResources.S3: os.environ.get("S3_LOCAL_URL", "http://localhost:8001"),
    }


class AppAttrs:
    PRACTICE_ADMIN = "Practice admin"
    BRANCH_ADMIN = "Branch admin"
    BRANCH = "Branch"
    PRACTICE = "Practice"
    RECORD = "Record"
