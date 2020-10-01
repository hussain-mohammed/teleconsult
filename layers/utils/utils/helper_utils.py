from string import Template

from itsdangerous import URLSafeSerializer

from .constants import Constants, CustomAttrs, Roles, StndAttrs
from .logger import logger


def generate_token(token):
    serializer = URLSafeSerializer(Constants.SECURED_URL_SECRET_KEY)
    encoded_token = serializer.dumps(token, salt=Constants.SECURITY_PASSWORD_SALT)
    return encoded_token


def read_template(template):
    with open(template, "r") as t:
        html_string = t.read()
        return html_string


def get_verification_custom_msg(template, user):
    context = {"name": user.get("name")}
    email_text = read_template(template)
    template_obj = Template(email_text)
    html_content = template_obj.substitute(**context)
    logger.debug(f"user get get signup invitation {html_content}")
    return html_content


def get_custom_invitation_msg(template, user):
    user_role = user.get(Roles.ROLE_ATTR_NAME)
    context = {"name": user.get("name"), "url": role_based_login.get(user_role)}
    email_text = read_template(template)
    template_obj = Template(email_text)
    html_content = template_obj.substitute(**context)
    logger.debug(f"user get custom invitation {html_content}")
    return html_content


def get_standard_attrs(payload):
    user = {}
    for user_attr in payload.get("UserAttributes"):
        name = user_attr.get("Name")
        if not name.startswith("custom:"):
            user[name] = user_attr.get("Value")
    user["member_since"] = payload.get("UserCreateDate").isoformat()
    return user


def remove_unwanted_attrs(payload):
    unwanted_attrs = [
        StndAttrs.EMAIL_VERIFIED,
        StndAttrs.PHONE_VERIFIED,
        StndAttrs.SUB,
        CustomAttrs.IS_DELETED,
        Constants.SK,
    ]
    for attr in unwanted_attrs:
        payload.pop(attr, None)
    return payload


role_based_login = {
    Roles.DOCTOR: f"{Constants.WEB_DOMAIN}doctor/signin",
    Roles.BRANCH_ADMIN: f"{Constants.WEB_DOMAIN}admin/signin",
    Roles.PRACTICE_ADMIN: f"{Constants.WEB_DOMAIN}admin/signin",
    Roles.PATIENT: f"{Constants.WEB_DOMAIN}patient/signin",
}
