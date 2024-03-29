from fastapi import APIRouter, Body, Depends, Request
from typing import Optional, List
import json

from rate_limiter import limiter

from utilities.methods import create_success_response
from _exceptions import route_exeception_handler, NotFoundError

from .model import StorageConnection


router = APIRouter()


@router.get("/connect")
@limiter.limit("5/minute")
@route_exeception_handler
def test_connection(request: Request):
    pass


@router.get("/sample/database")
@limiter.limit("5/minute")
@route_exeception_handler
def sample_database(request: Request):
    pass


@router.get("/sample/collection")
@limiter.limit("5/minute")
@route_exeception_handler
def sample_collection(request: Request):
    pass
