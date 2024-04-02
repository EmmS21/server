from fastapi import APIRouter, Body, Depends, Request
from typing import Optional, List
import json

from rate_limiter import limiter

from utilities.methods import create_success_response
from _exceptions import route_exeception_handler

from .service import PipelineAsyncService, process_orchestrator
from .tasks import process_pipeline
from .model import PipelineCreateRequest, PipelineResponse

router = APIRouter()

# pipelines collection
pipeline = {
    "enabled": True,
    "connection": {
        "engine": "mongodb",
        "host": "cluster-sandbox-1.cic7n4w.mongodb.net",
        "database": "sample_mflix",
        "username": "enrique",
        "password": "qeJeqY8FffriLbj1",
    },
    # "filters": {"status": "processing"},
    "on_operation": ["insert"],
    "collection": "documents",
    "source_destination_mappings": [
        {
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "source": {
                "name": "file_url",
                "type": "file_url",
                "settings": {},
            },
            "destination": {
                "collection": "theaters",
                "field": "file_elements",
                "embedding": "test_embedding_384",
            },
        }
    ],
}


# invoke pipeline
@router.post("/{pipeline_id}")
@route_exeception_handler
async def invoke_pipeline(request: Request, pipeline_id: str):
    payload = await request.json()
    pipeline_service = PipelineAsyncService(request.index_id)
    # pipeline = await pipeline_service.get_one({"pipeline_id": pipeline_id})

    # if not pipeline:
    #     raise NotFoundError("Pipeline not found.")

    if isinstance(payload, str):
        payload = json.loads(payload)

    # this accounts for insertions of embeddings by process_pipeline.
    # we don't want to re-run process_pipeline.
    if "file_url" in payload.get("fullDocument", {}) or "contents" in payload.get(
        "fullDocument", {}
    ):
        return {"task_id": task.id}

    task = process_pipeline.apply_async(
        kwargs={
            "index_id": request.index_id,
            "pipeline": pipeline,
            "payload": payload,
        }
    )

    return {"task_id": task.id}


# create pipeline
@router.post("/", response_model=PipelineResponse)
@route_exeception_handler
async def create_pipeline(
    request: Request,
    connection_id: str,
    pipeline_request: PipelineCreateRequest = Body(...),
):
    pipeline_service = PipelineAsyncService(request.index_id)
    return await pipeline_service.create(pipeline_request, connection_id)


@router.get("/status/{task_id}")
@route_exeception_handler
def task_status(request: Request, task_id: str):
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
# @route_exeception_handler
# async def list_pipelines(request: Request):
#     return create_success_response({"message": "Pipelines listed."})


# # modify pipeline
# @router.put("/{pipeline_id}")
# @route_exeception_handler
# async def modify_pipeline(request: Request):
#     return create_success_response({"message": "Pipeline modified."})
