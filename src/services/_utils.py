from fastapi.responses import JSONResponse
from typing import Optional
import psutil
from functools import wraps

from _exceptions import TooManyRequestsError


def create_json_response(
    success: bool, status: int, error: str, response: Optional[str]
):
    return JSONResponse(
        content={
            "success": success,
            "status": status,
            "error": error,
            "response": response,
        },
        status_code=status,
    )


def create_success_response(response: Optional[str]):
    return create_json_response(True, 200, "", response)


def check_cpu_usage(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        cpu_usage = psutil.cpu_percent()
        if cpu_usage > 90:
            raise TooManyRequestsError()
        return await func(*args, **kwargs)

    return wrapper
