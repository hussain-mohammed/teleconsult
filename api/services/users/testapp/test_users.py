import pytest

from users.services.users import UserService

from .resources import TableName, create_user_pool, ddb_setup, user_payload

user_service = UserService()


class TestClassDDB:
    @pytest.mark.parametrize("payload", user_payload)
    def test_create_user(self, cognito_client, payload):
        user_service.cognito_client = cognito_client
        with create_user_pool(cognito_client) as pool_id:
            user_service.user_pool_id = pool_id
            resp = user_service.create_user(payload)
            pytest.user = resp["Users"]["Username"]
        assert resp.get("status")

    def test_dynamodb_table(self, dynamodb_resource, dynamodb_client):
        # test the successfulcreation of a table
        with ddb_setup(dynamodb_resource):
            response = dynamodb_client.describe_table(TableName=TableName)
            assert response["Table"]["TableName"] == TableName

    def test_get_user(self, cognito_client, dynamodb_resource):
        user_table = dynamodb_resource.Table(TableName)
        user_service.cognito_client = cognito_client
        user_service.user_table = user_table
        with create_user_pool(cognito_client) as pool_id:
            user_service.user_pool_id = pool_id
            resp = user_service.get_user(pytest.user)
        assert resp.get("status")
