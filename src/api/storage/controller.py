from fastapi import APIRouter, Body, Depends, Request
from typing import Optional, List
import json

from rate_limiter import limiter

from utilities.methods import create_success_response
from _exceptions import route_exception_handler, NotFoundError

from .model import StorageConnection


router = APIRouter()


# mixpeek.storage.connect
@router.get(
    "/connect",
    openapi_extra={
        "x-fern-sdk-method-name": "connect",
        "x-fern-sdk-group-name": ["storage"],
    },
)
@limiter.limit("5/minute")
@route_exception_handler
def test_connection(request: Request):
    pass


# mixeek.storage.sample.database
@router.get(
    "/sample/database/{database_name}",
    openapi_extra={
        "x-fern-sdk-method-name": "database",
        "x-fern-sdk-group-name": ["storage", "sample"],
    },
)
@limiter.limit("5/minute")
@route_exception_handler
def sample_database(request: Request, database_name: str):
    pass


# mixeek.storage.sample.collection
@router.get(
    "/sample/collection/{collection_name}",
    openapi_extra={
        "x-fern-sdk-method-name": "collection",
        "x-fern-sdk-group-name": ["storage", "sample"],
    },
)
@limiter.limit("5/minute")
@route_exception_handler
def sample_collection(request: Request, collection_name: str):
    pass
