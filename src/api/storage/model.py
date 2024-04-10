from users.model import Connection
from pydantic import BaseModel
from utilities.helpers import PyObjectId


class StorageConnection(Connection):
    pass


class InsertResponse(BaseModel):
    url: str
    _id: PyObjectId

    class Config:
        extra = "allow"
