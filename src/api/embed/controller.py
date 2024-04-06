from fastapi import APIRouter, Request
from rate_limiter import limiter

from _exceptions import route_exception_handler


from .model import (
    EmbeddingRequest,
    EmbeddingResponse,
    ConfigsRequest,
    ConfigsResponse,
)

from .service import EmbeddingHandler

router = APIRouter()


# mixpeek.embed.config
@router.post(
    "/config",
    response_model=ConfigsResponse,
    openapi_extra={"x-fern-sdk-method-name": "get_model_config"},
)
@route_exception_handler
async def embed_config(request: Request, data: ConfigsRequest):
    embedding_handler = EmbeddingHandler()
    return await embedding_handler.get_configs(data)


# mixpeek.embed
@router.post(
    "/",
    response_model=EmbeddingResponse,
    openapi_extra={"x-fern-sdk-method-name": "embed"},
)
@route_exception_handler
async def embed(request: Request, data: EmbeddingRequest):
    embedding_handler = EmbeddingHandler()
    return await embedding_handler.encode(data)
