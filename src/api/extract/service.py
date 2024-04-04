import httpx
import json
import time

from config import services_url

from .model import ExtractRequest
from _exceptions import InternalServerError, NotFoundError, BadRequestError
from utilities.methods import create_success_response, _send_post_request

modality_to_content_types = {
    "text": [
        "application/pdf",
        "text/html",
        "text/html; charset=utf-8",
        "text/csv",
        "text/plain",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "text/markdown",
        "application/xml",
    ],
    "image": [
        "image/png",
        "image/jpeg",
        "image/gif",
        "image/bmp",
        "image/tiff",
        "image/webp",
    ],
    "audio": [
        "audio/mpeg",
        "audio/wav",
        "audio/ogg",
        "audio/flac",
        "audio/mp4",
        "audio/aac",
    ],
    "video": [
        "video/mp4",
        "video/x-msvideo",
        "video/quicktime",
        "video/x-ms-wmv",
        "video/x-flv",
    ],
}


class ExtractHandler:
    def __init__(self):
        pass

    async def _get_file_type(self, file_url):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.head(file_url)
                if response.status_code == 200:
                    content_type = response.headers.get("content-type")
                    if not content_type:
                        raise BadRequestError(
                            error={"message": "Content type not found"}
                        )
                    return content_type
                else:
                    raise BadRequestError(
                        error={"message": "Error retrieving file info"}
                    )

        except Exception:
            raise BadRequestError(error={"message": "Error downloading file info"})

    def _get_modality(self, content_type):
        for modality, content_types in modality_to_content_types.items():
            if content_type in content_types:
                return modality
        raise BadRequestError(
            error={"message": f"Content type {content_type} not recognized"}
        )

    async def parse(self, parser_request: ExtractRequest):
        # if there is no file_url then modality is automatically text
        if parser_request.file_url:
            content_type = await self._get_file_type(parser_request.file_url)
        else:
            content_type = "text/plain"

        modality = self._get_modality(content_type.lower())

        url = f"{services_url}/parse/{modality}"
        data = json.dumps(parser_request.model_dump())

        try:
            start_time = time.time()
            resp = await _send_post_request(url, data, timeout=180)
            resp["elapsed_time"] = time.time() - start_time
            return resp
        except Exception as e:
            raise InternalServerError(
                error={
                    "message": "There was an error with the request, reach out to support"
                }
            )
