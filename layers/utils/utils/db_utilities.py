from boto3.dynamodb.conditions import Attr

from utils.constants import AppAttrs

from .logger import logger
from .response import ResponseMessage


class DBUtilities:
    def __init__(self, table_obj=None):
        self.table_obj = table_obj

    def filter_attributes(self, data, fields, updateable_field_flag):
        if updateable_field_flag:
            attributes = {k: data[k] for k in data if k in fields}.keys()
        else:
            attributes = {k: data[k] for k in data if k not in fields}.keys()
        return attributes

    def build_update_params(self, data, attributes):
        """
        arranging all the parameters for updating a record
        :param data: dict
        :return: tuple
        """
        update_expression = "set "
        expression_attribute_names = {}
        expressionAttribute_values = {}
        for index, attributeName in enumerate(attributes):
            attrib_key = f"#attr{index}"
            value_key = f":val{index}"
            expression_to_add = f"{attrib_key} = {value_key}"
            if index == 0:
                update_expression += expression_to_add
            else:
                update_expression += f",{expression_to_add}"
            expression_attribute_names[attrib_key] = attributeName
            expressionAttribute_values[value_key] = data[attributeName]

        if update_expression == "set":
            # This means we have nothing to update, so return null
            update_expression = None
        return {
            "UpdateExpression": update_expression,
            "ExpressionAttributeNames": expression_attribute_names,
            "ExpressionAttributeValues": expressionAttribute_values,
        }

    def list_items(self):
        response = self.table_obj.scan(FilterExpression=Attr("is_deleted").eq("false"))

        items = response["Items"]
        resp = {"status": True, "items": items}
        logger.info("record fetched successfully!")
        return resp

    def get_item(self, key: dict):
        """
        method to fetch records from the database
        :param key: primary key (partition key)
        :param table: name of the table
        :return:
        """
        response = self.table_obj.get_item(Key=key)

        item = response.get("Item")
        resp = {
            "item": {},
            "message": ResponseMessage.ENTITY_FETCHED.format(AppAttrs.RECORD),
        }
        if item:
            resp["item"] = item
        else:
            resp["message"] = ResponseMessage.KEY_ERROR_MSG
        logger.info(ResponseMessage.ENTITY_FETCHED.format(AppAttrs.RECORD))
        return resp

    def insert_item(self, items):
        """
        method to put items in the database
        :param items: data to be inserted
        :return:
        """
        self.table_obj.put_item(Item=items)
        resp = {
            "status": True,
            "message": ResponseMessage.ENTITY_ADDED.format(AppAttrs.RECORD),
            "item": items,
        }
        logger.info(ResponseMessage.ENTITY_ADDED.format(AppAttrs.RECORD))
        return resp

    def update_item(self, key: dict, items, attrs):
        """
        method to update a record in database
        :param key: partition key
        :param data: records to be updated
        :return:
        """
        update_params = self.build_update_params(items, attrs)
        if not update_params["UpdateExpression"]:
            return {"status": True, "message": ResponseMessage.NO_UPDATE_MSG}
        self.table_obj.update_item(
            Key=key,
            UpdateExpression=update_params["UpdateExpression"],
            ExpressionAttributeNames=update_params["ExpressionAttributeNames"],
            ExpressionAttributeValues=update_params["ExpressionAttributeValues"],
            ConditionExpression="attribute_exists(pk)",
            ReturnValues="ALL_NEW",
        )
        resp = {
            "status": True,
            "message": ResponseMessage.ENTITY_UPDATED.format(AppAttrs.RECORD),
        }
        logger.info(ResponseMessage.ENTITY_UPDATED.format(AppAttrs.RECORD))
        return resp
