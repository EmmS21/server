from fastapi import APIRouter, Request
from rate_limiter import limiter

from .model import GenerationResponse, GenerationRequest
from .service import generate_orchestrator

from _exceptions import route_exception_handler


router = APIRouter()


# mixpeek.generate.text
@router.post(
    "/text",
    response_model=GenerationResponse,
    openapi_extra={"x-fern-sdk-method-name": "base_generate"},
)
@route_exception_handler
@limiter.limit("10/minute")
async def generate_text_api(request: Request, generate: GenerationRequest):
    generate_request = await generate_orchestrator(generate)
    return generate_request
