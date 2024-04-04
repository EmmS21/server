from fastapi import APIRouter, Body, Depends, Request
from typing import List, Optional
from rate_limiter import limiter

from _exceptions import route_exception_handler


from utilities.helpers import generate_uuid, current_time
from utilities.code import CodeValidation

from .model import (
    WorkflowCreateRequest,
    WorkflowSchema,
    WorkflowResponse,
    WorkflowCodeResponse,
)
from .service import WorkflowSyncService
from .invoke import invoke_handler

from db.model import PaginationParams

router = APIRouter()


# mixpeek.workflow.create
@router.post(
    "/",
    response_model=WorkflowResponse,
    openapi_extra={
        "x-fern-sdk-method-name": "create",
        "x-fern-sdk-group-name": ["workflow"],
    },
)
@route_exception_handler
async def create_workflow(
    request: Request, workflow_request: WorkflowCreateRequest = Body(...)
):
    workflow_service = WorkflowSyncService(request.index_id)
    return workflow_service.create(workflow_request)


# mixpeek.workflow.invoke
@router.post(
    "/{workflow_id}/invoke",
    openapi_extra={
        "x-fern-sdk-method-name": "invoke",
        "x-fern-sdk-group-name": ["workflow"],
    },
)
@limiter.limit("10/minute")
@route_exception_handler
async def invoke_workflow(
    request: Request,
    workflow_id: str,
    parameters: dict = Body(...),
    websocket_id: Optional[str] = None,
):

    workflow_service = WorkflowSyncService(request.index_id)
    workflow = workflow_service.get_and_validate(workflow_id)

    # run invokation
    result = await invoke_handler(
        serverless_name=workflow["metadata"]["serverless_function_name"],
        run_id=generate_uuid(),
        websocket_id=websocket_id,
        request_parameters=parameters,
    )

    workflow_service.update(workflow_id, {"last_run": current_time()})

    return result


# mixpeek.workflow.code
@router.post(
    "/code",
    response_model=WorkflowCodeResponse,
    openapi_extra={
        "x-fern-sdk-method-name": "code",
        "x-fern-sdk-group-name": ["workflow"],
    },
)
@route_exception_handler
async def convert_code_to_string(code: str = Body(...)):
    return {"code_as_string": code}
