from fastapi import APIRouter, Body, Depends, Request, File, Form, UploadFile
from typing import Optional, List
import json

from rate_limiter import limiter

from _exceptions import route_exception_handler, NotFoundError

from .model import StorageConnection, InsertResponse


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


# mixpeek.storage.insert
@router.post(
    "/insert-one",
    response_model=InsertResponse,
    openapi_extra={
        "x-fern-sdk-method-name": "insert_one",
        "x-fern-sdk-group-name": ["storage"],
    },
)
@route_exception_handler
async def insert_one(request: Request, file: UploadFile = File(...)):
    form_data = await request.form()
    # `file` is already captured as UploadFile, remove it from form_data if present
    form_data = {k: v for k, v in form_data.items() if k != "file"}
    # Process file
    content = await file.read()
    # Now `form_data` contains all other form fields as arbitrary key-value pairs
    response_data = {"url": "123", "_id": "123", **form_data}
    return response_data


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
