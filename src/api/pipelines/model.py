from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

from utilities.helpers import unique_name, generate_uuid, current_time
from utilities.encryption import SecretCipher

from users.model import Connection


# Enumerations
class FieldType(str, Enum):
    file_url = "file_url"
    contents = "contents"


class Source(BaseModel):
    field: str
    type: FieldType
    settings: dict


class Destination(BaseModel):
    collection: str
    field: str
    embedding: str


class SourceDestinationMapping(BaseModel):
    embedding_model: str
    source: Source
    destination: Destination


class Pipeline(BaseModel):
    pipeline_id: str = Field(default_factory=lambda: generate_uuid(6, False))
    enabled: bool = False

    connection: Optional[Connection]
    source_destination_mappings: List[SourceDestinationMapping]
    metadata: Optional[dict]

    # internal keys
    created_at: datetime = Field(default_factory=lambda: current_time())
    last_run: Optional[datetime] = Field(None)


# requests
"""Requests"""


# Pipeline schema definition
class PipelineCreateRequest(BaseModel):
    source_destination_mappings: List[SourceDestinationMapping]
    metadata: Optional[dict] = {}


class PipelineConnection(Connection):
    pass


"""responses"""


class PipelineResponse(Pipeline):
    pass


# class PipelineResponse(BaseModel):
#     pipeline_id: str
#     created_at: datetime
#     last_run: Optional[datetime]
#     enabled: bool
#     connection: Connection
#     source: SourceSchema
#     destination: DestinationSchema
#     metadata: Optional[dict] = {}
