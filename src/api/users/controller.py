from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional, Union, cast

from auth.service import get_index_id
from _exceptions import NotFoundError, route_exception_handler

from .model import User, UserRequest, UpdateUserRequest
from .service import UserService

from config import mixpeek_admin_token

router = APIRouter()


# private
@router.post("/private", response_model=User, include_in_schema=False)
@route_exception_handler
async def create_user_private(user: UserRequest, Authorization: str = Header(None)):
    if Authorization != mixpeek_admin_token:
        raise NotFoundError("Invalid admin token")

    user_service = UserService()
    return user_service.create_user(user)


# public
@router.get("/", response_model=User)
@route_exception_handler
async def get_user(index_id: str = Depends(get_index_id)):
    user_service = UserService()
    return user_service.get_user_by_index_id(index_id)


@router.put("/", response_model=User)
@route_exception_handler
async def update_user(update: UpdateUserRequest, index_id: str = Depends(get_index_id)):
    user_service = UserService()
    return user_service.update_user(index_id, update.model_dump(exclude_unset=True))
