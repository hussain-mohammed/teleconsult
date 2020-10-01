import os


class LocalURI:
    CREATE_PRESIGNED_POST = DOWNLOAD_PRESIGNED = "/documents/urls"


class LocalConstants:
    DATA_BUCKET = os.environ.get("DATA_BUCKET")
    UPLOAD_EXPIRATION = os.environ.get("UPLOAD_EXPIRATION")
    DOWNLOAD_EXPIRATION = os.environ.get("DOWNLOAD_EXPIRATION")
    ROLE = "role"
    FILE_EXT = "fileext"
    PROFILE = "profile"
