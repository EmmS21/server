from fastapi import APIRouter, Body, Depends, Request
from typing import Optional, List
import json

from rate_limiter import limiter

from _exceptions import route_exception_handler, NotFoundError

from .service import PipelineAsyncService, process_orchestrator
from .tasks import process_pipeline
from .model import (
    PipelineCreateRequest,
    PipelineResponse,
    PipelineConnection,
    PipelineTaskResponse,
)

router = APIRouter()

# pipelines collection
# mongodb+srv://sandbox:UT086Nt4m1V2DMRA@sandbox.mhsby.mongodb.net/
pipeline = {
    "enabled": True,
    # "connection": {
    #     "engine": "mongodb",
    #     "host": "sandbox.mhsby.mongodb.net",
    #     "database": "use_cases",
    #     "username": "sandbox",
    #     "password": "UT086Nt4m1V2DMRA",
    # },
    # "filters": {"status": "processing"},
    # "on_operation": ["insert"],
    # "collection": "documents",
    "source_destination_mappings": [
        {
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "source": {
                "name": "resume_url",
                "type": "file_url",
                "settings": {},
            },
            "destination": {
                "collection": "resume_embeddings",
                "field": "text",
                "embedding": "embedding",
            },
        }
    ],
}


# mixpeek.pipeline.invoke
@router.post(
    "/{pipeline_id}",
    response_model=PipelineTaskResponse,
    openapi_extra={
        "x-fern-sdk-method-name": "invoke",
        "x-fern-sdk-group-name": ["pipeline"],
    },
)
@route_exception_handler
async def invoke(request: Request, pipeline_id: str):
    payload = await request.json()
    index_id = request.index_id  # type: ignore
    pipeline_service = PipelineAsyncService(index_id)
    pipeline = await pipeline_service.get_one({"pipeline_id": pipeline_id})

    if not pipeline:
        raise NotFoundError({"error": "Pipeline not found."})

    if isinstance(payload, str):
        payload = json.loads(payload)

    task = process_pipeline.apply_async(
        kwargs={
            "index_id": index_id,
            "pipeline": pipeline,
            "payload": payload,
        }
    )

    return {"task_id": task.id}


# mixpeek.pipeline.create
@router.post(
    "/",
    response_model=PipelineResponse,
    openapi_extra={
        "x-fern-sdk-method-name": "create",
        "x-fern-sdk-group-name": ["pipeline"],
    },
)
@route_exception_handler
async def create(
    request: Request,
    pipeline_request: PipelineCreateRequest = Body(...),
):
    pipeline_service = PipelineAsyncService(request.index_id)
    return await pipeline_service.create(pipeline_request)


# mixpeek.pipeline.get
@router.get(
    "/{pipeline_id}",
    response_model=PipelineResponse,
    openapi_extra={
        "x-fern-sdk-method-name": "get",
        "x-fern-sdk-group-name": ["pipeline"],
    },
)
@route_exception_handler
async def get(
    request: Request,
    pipeline_id: str,
):
    pipeline_service = PipelineAsyncService(request.index_id)
    return await pipeline_service.get_one({"pipeline_id": pipeline_id})


# mixpeek.pipeline.status
@router.get(
    "/status/{task_id}",
    openapi_extra={
        "x-fern-sdk-method-name": "status",
        "x-fern-sdk-group-name": ["pipeline"],
    },
)
@route_exception_handler
def status(request: Request, task_id: str):
    """Query tasks status."""
    task = process_pipeline.AsyncResult(task_id)
    if task.state == "PENDING":
        response = {
            "state": task.state,
            "status": "Pending...",
        }
    elif task.state == "FAILURE":
        response = {
            "state": task.state,
            # "current": task.info.get("current", 0),
            # "total": task.info.get("total", 1),
            "status": "Failed...",
        }
    else:
        response = {
            "state": task.state,
            # "current": 1,
            # "total": 1,
            "status": str(task.info),
        }
    return response


# # list pipelines
# @router.get("/")
# @route_exception_handler
# async def list_pipelines(request: Request):
#     return create_success_response({"message": "Pipelines listed."})


# # modify pipeline
# @router.put("/{pipeline_id}")
# @route_exception_handler
# async def modify_pipeline(request: Request):
#     return create_success_response({"message": "Pipeline modified."})
