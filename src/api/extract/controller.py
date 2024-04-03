from fastapi import APIRouter
from _exceptions import route_exception_handler

from .model import ExtractRequest, ExtractResponse
from .service import ParseHandler


router = APIRouter()


# mixpeek.extract
@router.post(
    "/",
    response_model=ExtractResponse,
    openapi_extra={
        "x-fern-sdk-method-name": "extract",
        # "x-fern-sdk-group-name": ["extract"],
    },
)
@route_exception_handler
async def extract(
    parser_request: ExtractRequest,
):
    parse_handler = ParseHandler()
    return await parse_handler.parse(parser_request)
