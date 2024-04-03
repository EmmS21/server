from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
import logging
import traceback


from _exceptions import (
    InternalServerError,
    NotFoundError,
    BadRequestError,
)
from utilities.methods import create_json_response
from config import server_env, sentry_dsn

from rate_limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


from api import api_router


app = FastAPI(
    openapi_url="/docs/openapi.json",
    title="Mixpeek API",
    servers=[{"url": "https://api.mixpeek.com/"}],
)


# Add the limiter as a middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(InternalServerError)
async def internal_server_exception_handler(request: Request, exc: InternalServerError):
    return create_json_response(exc.success, exc.status, exc.error, exc.response)


@app.exception_handler(NotFoundError)
async def not_found_exception_handler(request: Request, exc: NotFoundError):
    return create_json_response(exc.success, exc.status, exc.error, exc.response)


@app.exception_handler(BadRequestError)
async def bad_request_exception_handler(request: Request, exc: BadRequestError):
    return create_json_response(exc.success, exc.status, exc.error, exc.response)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return create_json_response(False, 422, exc.errors(), None)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
