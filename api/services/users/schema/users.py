from marshmallow import (
    Schema,
    SchemaOpts,
    ValidationError,
    fields,
    post_load,
    pre_load,
    validate,
    validates_schema,
)

from utils.constants import CustomAttrs, Roles, StndAttrs
from utils.response import ResponseMessage


class BaseSchemaOpts(SchemaOpts):
    """Option class for Base Schema"""

    def __init__(self, meta, ordered=False):
        super().__init__(meta, ordered=ordered)
        self.update_fields = getattr(meta, "update_fields", set())


class BaseSchema(Schema):
    """Base schema class to check updatable fields"""

    OPTIONS_CLASS = BaseSchemaOpts

    @pre_load
    def check_update_fields(self, data, many=False, partial=True):
        non_update_fields = set(self.fields) - set(self.opts.update_fields)
        return {
            key: value for key, value in data.items() if key not in non_update_fields
        }


class AddressSchema(Schema):
    door = fields.Str(required=True)
    street = fields.Str(required=True)
    city = fields.Str(required=True)
    state = fields.Str()
    zipcode = fields.Str(required=True)


class DoctorUpdateSchema(BaseSchema):
    pk = fields.Str(required=True)
    role = fields.Str(required=True)
    DEA = fields.Str(required=True)
    NPI = fields.Str(required=True)
    email = fields.Email(required=True)
    phone_number = fields.Str(required=True)
    address = fields.Nested(AddressSchema)
    is_cvo_verified = fields.Boolean(required=True)
    name = fields.Str(required=True)
    specialities = fields.Str(required=True)
    member_since = fields.Str(required=True)
    education = fields.Str()
    experience = fields.Integer()
    operational_days = fields.List(
        fields.Str(), required=True, validate=validate.Length(1, 7)
    )
    operational_hours = fields.List(
        fields.Str(), required=True, validate=validate.Length(2)
    )
    consultation_slot = fields.Integer(required=True)
    profile_pic = fields.Str()
    user_tz = fields.Str(required=True)

    @post_load()
    def change_operational_days_to_upper_case(self, data, **kwargs):
        days = data["operational_days"]
        data["operational_days"] = list(map(lambda day: day.lower(), days))
        return data

    class Meta:
        update_fields = (
            "specialities",
            "address",
            "education",
            "experience",
            "operational_days",
            "operational_hours",
            "consultation_slot",
            "user_tz",
        )


class PatientUpdateSchema(BaseSchema):
    pk = fields.Str(required=True)
    role = fields.Str(required=True)
    email = fields.Email(required=True)
    phone_number = fields.Str(required=True)
    address = fields.Nested(AddressSchema)
    name = fields.Str(required=True)
    member_since = fields.Str(required=True)
    profile_pic = fields.Str()
    user_tz = fields.Str(required=True)

    class Meta:
        update_fields = ("address", "user_tz")


class UserSchema(Schema):
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    phone_number = fields.Str(required=True)
    role = fields.Str(required=True)
    message_action = fields.Bool()

    @validates_schema
    def is_role_valid(self, data, **kwargs):
        """'value is the role of practice admin parsed from is_role_valid by marshmallow"""
        role = self.context.get(CustomAttrs.ROLE)
        if data[CustomAttrs.ROLE].upper() != role:
            raise ValidationError(ResponseMessage.USER_ROLE_MSG)

    @post_load()
    def get_cognito_attrs(self, data, **kwargs):
        """
        this will unpack the payload given by client

        Args:
            payload (dict): contains the user details to create user.
        """
        message_action = data.pop("message_action", None)
        email = data.get(StndAttrs.EMAIL)

        # preparing a list of dictionary for payload using list comprehenssion
        user_attrs = [
            {"Name": name, "Value": value}
            if name != CustomAttrs.ROLE
            else {"Name": Roles.ROLE_ATTR_NAME, "Value": value.upper()}
            for name, value in data.items()
        ]
        user_attrs.append({"Name": StndAttrs.EMAIL_VERIFIED, "Value": "true"})

        return {
            "message_action": message_action,
            "email": email,
            "user_attrs": user_attrs,
        }


doctor_update_schema = DoctorUpdateSchema()
create_user_schema = UserSchema()
patient_update_schema = PatientUpdateSchema()
