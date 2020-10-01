from constants import LocalConstants
from utils.logger import logger
from utils.response import ResponseMessage


class DocumentService:
    def __init__(self, s3_client=None):
        self.s3_client = s3_client

    def get_upload_presigned_url(self, user_id, role, fileext):
        bucket = LocalConstants.DATA_BUCKET
        key = f"users/{role}_{user_id}.{fileext}"
        field = {"x-amz-meta-user_id": user_id}
        condition = [{"x-amz-meta-user_id": user_id}]
        resp = self.s3_client.generate_presigned_post(
            bucket,
            key,
            Fields=field,
            Conditions=condition,
            ExpiresIn=int(LocalConstants.UPLOAD_EXPIRATION),
        )
        logger.debug(resp)
        return {
            "data": resp,
            "status": True,
            "message": ResponseMessage.ENTITY_FETCHED.format("Url"),
        }

    def get_download_presigned_url(self, s3key, _type):
        params = {"Bucket": LocalConstants.DATA_BUCKET}
        if _type == LocalConstants.PROFILE:
            params["Key"] = f"users/{s3key}"
        resp = self.s3_client.generate_presigned_url(
            "get_object", params, ExpiresIn=int(LocalConstants.DOWNLOAD_EXPIRATION)
        )
        logger.debug(resp)
        return {
            "data": resp,
            "status": True,
            "message": ResponseMessage.ENTITY_FETCHED.format("Url"),
        }
