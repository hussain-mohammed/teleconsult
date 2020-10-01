from flask import Flask, request

from constants import LocalConstants, LocalURI
from utils.aws_clients import AWSConnections
from utils.constants import AwsResources, Constants, HttpVerbs
from utils.response import CustomResponse, Status
from services import DocumentService

app = Flask(__name__)

s3_client = AWSConnections(AwsResources.S3).get_client()
document_service = DocumentService(s3_client=s3_client)


@app.route(LocalURI.CREATE_PRESIGNED_POST, methods=[HttpVerbs.POST])
def create_presigned_post_url():
    response = CustomResponse()
    user_id = request.json.get(Constants.UID)
    role = request.json.get(LocalConstants.ROLE)
    fileext = request.json.get(LocalConstants.FILE_EXT)
    presigned_url = document_service.get_upload_presigned_url(user_id, role, fileext)
    if not presigned_url.get(Constants.STATUS):
        response.status = Status.HTTP_400_BAD_REQUEST
    response.set_entities(presigned_url)
    return response.get_response()


@app.route(LocalURI.DOWNLOAD_PRESIGNED, methods=[HttpVerbs.GET])
def get_documents():
    response = CustomResponse()
    s3_key = request.args.get("s3_key")
    _type = request.args.get("type")
    presigned_url = document_service.get_download_presigned_url(s3_key, _type)
    if not presigned_url.get(Constants.STATUS):
        response.status = Status.HTTP_400_BAD_REQUEST
    response.set_entities(presigned_url)
    return response.get_response()
