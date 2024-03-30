from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional, Union, cast

from auth.service import get_index_id
from _exceptions import NotFoundError

from .model import User, UserRequest
from .service import UserService

from config import mixpeek_admin_token

router = APIRouter()


@router.post("/", response_model=User, include_in_schema=False)
def create_user(user: UserRequest, Authorization: str = Header(None)):
    if Authorization != mixpeek_admin_token:
        raise NotFoundError("Invalid admin token")

    user_service = UserService()
    return user_service.create_user(user)


# @router.put("/", response_model=TrustedOrgResponse, include_in_schema=False)
# def update_organization(
#     updates: OrganizationUpdateRequest, index_id: str = Depends(get_index_id)
# ):
#     service = OrganizationSyncService()
#     updates_dict = updates.model_dump(exclude_unset=True)
#     return service.update_organization(index_id, updates_dict)


# @router.get("/", response_model=OrganizationBase, include_in_schema=False)
# def get_organization(index_id: str = Depends(get_index_id)):
#     service = OrganizationSyncService()
#     return service.get_organization(index_id)


# @router.post("/secrets")
# def add_secret(secret: SecretRequest, index_id: str = Depends(get_index_id)):
#     organization_service = OrganizationSyncService()

#     try:
#         organization_service.add_secret(index_id, secret.name, secret.value)
#         return {"message": "Secret added successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.delete("/secrets")
# def delete_secret(secret_name: str, index_id: str = Depends(get_index_id)):
#     organization_service = OrganizationSyncService()

#     try:
#         organization_service.delete_secret(index_id, secret_name)
#         return {"message": "Secret deleted successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
