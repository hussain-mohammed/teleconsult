from flask import request

from .response import ResponseMessage


def get_current_user_id():
    """
        used to get the sub id of a current authenticated user from within the flask request.
    """
    user_sub = request.environ["serverless.event"]["requestContext"]["identity"][
        "cognitoAuthenticationProvider"
    ].split(":CognitoSignIn:")[1]
    user_id = f"user#{user_sub}"
    return user_id


def add_user_to_group(cognito_client, user_pool_id, username, user_group) -> dict:
    """Adds a user to designated group

    Args:
        cognito_client (object): Cognito client object.
        user_pool_id (str): user pool id of where user needs to be added.
        username (object): Created user object.

    Returns:
        dict: A response dictionary with following keys:
                status: bool  - Indicates if the request was successful
                data: object - Data object if any
                message: str - Response message
    """
    cognito_client.admin_add_user_to_group(
        UserPoolId=user_pool_id, Username=username, GroupName=user_group,
    )

    return {
        "status": True,
        "data": {},
        "message": ResponseMessage.USER_ADDED_SUCCESS,
    }


def get_dict_user_attributes(payload, replace_custom=False):
    user = {}
    for user_attr in payload.get("UserAttributes"):
        name = user_attr.get("Name")
        if replace_custom and name.startswith("custom:"):
            name = name.replace("custom:", "")
        user[name] = user_attr.get("Value")
    user["username"] = payload.get("Username")
    user["status"] = payload.get("UserStatus")
    return user


def get_cognito_user_profile(user_id, cognito_client, user_pool_id):
    """get user profile from the cognito

    Args:
        user_id (str): user's user id
    """

    cognito_response = cognito_client.admin_get_user(
        UserPoolId=user_pool_id, Username=user_id
    )
    user_attrs = get_dict_user_attributes(cognito_response, replace_custom=True)
    return user_attrs
