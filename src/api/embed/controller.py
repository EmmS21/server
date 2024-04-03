from fastapi import APIRouter, Request

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
async def embed_config(data: ConfigsRequest):
    embedding_handler = EmbeddingHandler(data.modality, data.model)
    return await embedding_handler.get_configs()


# mixpeek.embed
@router.post(
    "/",
    response_model=EmbeddingResponse,
    openapi_extra={"x-fern-sdk-method-name": "embed"},
)
@route_exception_handler
async def embed(data: EmbeddingRequest):
    embedding_handler = EmbeddingHandler(data.modality, data.model)
    return await embedding_handler.encode(data.model_dump())
