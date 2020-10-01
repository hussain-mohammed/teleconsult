import boto3

from .constants import Constants, EnvironVariables


class AWSConnections:
    def __init__(self, resource_name):
        self.resource = resource_name

    def get_client(self):
        client = boto3.client(self.resource)
        if Constants.IS_OFFLINE:
            client = boto3.client(
                self.resource, endpoint_url=EnvironVariables.LOCAL_URLS[self.resource]
            )
        return client

    def get_resource(self):
        client = boto3.resource(self.resource)
        if Constants.IS_OFFLINE:
            client = boto3.resource(
                self.resource, endpoint_url=EnvironVariables.LOCAL_URLS[self.resource]
            )
        return client
