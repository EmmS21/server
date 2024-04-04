import httpx
import json
import time

from config import services_url

from _exceptions import InternalServerError, NotFoundError, BadRequestError
from utilities.methods import _send_post_request

from .model import EmbeddingRequest, ConfigsRequest


class EmbeddingHandler:
    def __init__(self):
        pass

    async def encode(self, data: EmbeddingRequest):
        url = f"{services_url}/embed/{data.modality}"
        payload = {"model": data.model, **data.model_dump()}
        try:
            start_time = time.time() * 1000
            resp = await _send_post_request(url, json.dumps(payload))
            resp["elapsed_time"] = time.time() * 1000 - start_time
            return resp
        except Exception as e:
            raise InternalServerError(error={"message": str(e)})

    async def get_configs(self, data: ConfigsRequest):
        """
        accepts
            modality: Optional[Modality] = "text"
            model: Optional[str] = "sentence-transformers/all-MiniLM-L6-v2"
        """
        url = f"{services_url}/embed/{data.modality}/config"
        payload = {"model": data.model, "modality": data.modality}
        try:
            start_time = time.time() * 1000
            resp = await _send_post_request(url, json.dumps(payload))
            resp["elapsed_time"] = time.time() * 1000 - start_time
            return resp
        except Exception as e:
            raise InternalServerError(
                error={
                    "message": "There was an error with the request, reach out to support"
                }
            )
