from fastapi import APIRouter

from .model import ParseFileRequest
from .service import ParseHandler
from _exceptions import route_exeception_handler
from _utils import check_cpu_usage


router = APIRouter()


@router.post("/{modality}")
@check_cpu_usage
@route_exeception_handler
async def parse_file(
    modality: str,
    parser_request: ParseFileRequest,
):
    parse_handler = ParseHandler(parser_request.file_url, parser_request.contents)
    return await parse_handler.parse(modality=modality, parser_request=parser_request)
