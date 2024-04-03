from fastapi import APIRouter
from _exceptions import route_exception_handler

from .model import ParseFileRequest
from .service import ParseHandler


router = APIRouter()


@router.post("/")
@route_exception_handler
async def extract_file(
    parser_request: ParseFileRequest,
):
    parse_handler = ParseHandler()
    return await parse_handler.parse(parser_request)
