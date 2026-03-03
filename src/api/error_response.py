import json

from starlette.responses import PlainTextResponse
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_406_NOT_ACCEPTABLE,
    HTTP_400_BAD_REQUEST,
    HTTP_501_NOT_IMPLEMENTED,
    HTTP_500_INTERNAL_SERVER_ERROR,
)


def response_error_handler(result):
    status = result.get("status")
    details = result.get("details")

    if status == 400:
        return http_400_bad_request(details)
    elif status == 404:
        return http_404_not_found(details)
    elif status == 406:
        return http_406_not_acceptable(details)
    elif status == 500:
        return http_500_internal_server_error(details)
    elif status == 501:
        return http_501_not_implemented(details)
    else:
        return http_unknown_error(result)


def http_unknown_error(result):
    response_msg = json.dumps({"status_code": result["status"], "details": "Unknown"})
    return PlainTextResponse(response_msg, status_code=result["status"])


def http_400_bad_request(details: str = "Bad Request"):
    response_msg = json.dumps({
        "status_code": HTTP_400_BAD_REQUEST,
        "details": details
    })
    return PlainTextResponse(response_msg, status_code=HTTP_400_BAD_REQUEST)


def http_404_not_found(details: str = "Not Found"):
    response_msg = json.dumps({
        "status_code": HTTP_404_NOT_FOUND,
        "details": details
    })
    return PlainTextResponse(response_msg, status_code=HTTP_404_NOT_FOUND)


def http_406_not_acceptable(details: str = "Not Acceptable"):
    response_msg = json.dumps({
        "status_code": HTTP_406_NOT_ACCEPTABLE,
        "details": details
    })
    return PlainTextResponse(response_msg, status_code=HTTP_406_NOT_ACCEPTABLE)


def http_501_not_implemented(details: str = "Not Implemented"):
    response_msg = json.dumps({
        "status_code": HTTP_501_NOT_IMPLEMENTED,
        "details": details
    })
    return PlainTextResponse(response_msg, status_code=HTTP_501_NOT_IMPLEMENTED)


def http_500_internal_server_error(details: str = "Internal Server Error"):
    response_msg = json.dumps({
        "status_code": HTTP_500_INTERNAL_SERVER_ERROR,
        "details": details
    })
    return PlainTextResponse(response_msg, status_code=HTTP_500_INTERNAL_SERVER_ERROR)
