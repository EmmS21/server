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
    field: str = Field(..., description="The field name")
    type: FieldType = Field(..., description="The type of the field")
    settings: dict = Field(..., description="The settings for the field")


class Destination(BaseModel):
    collection: str = Field(..., description="The collection name")
    field: str = Field(..., description="The field name")
    embedding: str = Field(..., description="The embedding")


class SourceDestinationMapping(BaseModel):
    embedding_model: str = Field(..., description="The embedding model")
    source: Source = Field(..., description="The source")
    destination: Destination = Field(..., description="The destination")


class Pipeline(BaseModel):
    pipeline_id: str = Field(
        default_factory=lambda: generate_uuid(6, False),
        description="The ID of the pipeline",
    )
    enabled: Optional[bool] = Field(
        default=True, description="Whether the pipeline is enabled"
    )

    connection: Optional[Connection] = Field(None, description="The connection")
    source_destination_mappings: List[SourceDestinationMapping] = Field(
        ..., description="The source-destination mappings"
    )
    metadata: Optional[dict] = Field(None, description="The metadata")

    # internal keys
    created_at: datetime = Field(
        default_factory=lambda: current_time(), description="The creation time"
    )
    last_run: Optional[datetime] = Field(default=None, description="The last run time")


# requests
"""Requests"""


# Pipeline schema definition
class PipelineCreateRequest(BaseModel):
    source_destination_mappings: List[SourceDestinationMapping] = Field(
        ..., description="The source-destination mappings"
    )
    metadata: Optional[dict] = Field(None, description="The metadata")


class PipelineConnection(Connection):
    pass


"""responses"""


class PipelineResponse(Pipeline):
    pass


class PipelineTaskResponse(BaseModel):
    task_id: str = Field(..., description="The ID of the task")
